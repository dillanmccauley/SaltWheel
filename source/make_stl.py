"""Export print-ready STL files.

Threaded parts are meshed with manifold3d: the thread is built directly as a fine twisted
extrusion (720 points per turn, 0.05 mm slices), because CAD tessellators approximate
helical surfaces too coarsely for a 0.25 mm thread clearance. Everything else is
tessellated from the CadQuery models in build_parts.py.

Run:  python3 make_stl.py <outdir>
"""
import math, os, sys, tempfile
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, Mesh

sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "out"] + sys.argv[2:]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_parts.py")).read().split("if __name__")[0])

TMP = tempfile.mkdtemp()

def to_manifold(obj):
    p = os.path.join(TMP, "t.stl")
    cq.exporters.export(obj, p, tolerance=0.01, angularTolerance=0.05)
    t = trimesh.load(p); t.merge_vertices()
    return Manifold(Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32),
                         tri_verts=np.asarray(t.faces, dtype=np.uint32)))

def thread_solid(base, z_start, h, n=720, dz=0.05):
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = base + DEPTH * tri_soft((z_start - Z0 - LEAD * th / (2 * math.pi)) / PITCH)
        pts.append((r * math.cos(th), r * math.sin(th)))
    cs = CrossSection([pts])
    m = Manifold.extrude(cs, h, n_divisions=max(1, int(round(h / dz))), twist_degrees=360.0 * h / LEAD)
    return m.translate((0, 0, z_start))

def thread_error(m, base, zlo, zhi):
    """Max radial deviation of the meshed thread surface from the ideal profile."""
    mesh = m.to_mesh(); v = np.asarray(mesh.vert_properties)[:, :3]
    t = trimesh.Trimesh(v, np.asarray(mesh.tri_verts))
    pts, _ = trimesh.sample.sample_surface(t, 200000, seed=1)
    r = np.hypot(pts[:, 0], pts[:, 1]); th = np.arctan2(pts[:, 1], pts[:, 0]); z = pts[:, 2]
    sel = (r > base + 0.08) & (r < base + DEPTH - 0.08) & (z > zlo) & (z < zhi)
    ideal = np.array([base + DEPTH * tri_soft((zz - Z0 - LEAD * a / (2 * math.pi)) / PITCH) for zz, a in zip(z[sel], th[sel])])
    d = r[sel] - ideal
    return float(np.abs(d).max())

def save(m, path, flip=False):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    if flip:
        t.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    t.merge_vertices()
    t.apply_translation([0, 0, -t.bounds[0][2]])
    t.export(path)
    return t

def body_mesh():
    m = to_manifold(body_shell()) + thread_solid(MALE_ROOT, -BODY_H, SHOULDER_Z + BODY_H + 0.05)
    m = m - to_manifold(male_chamfer().union(cavity()))
    m = m + to_manifold(body_extras())
    return m - to_manifold(body_cuts())

def lid_mesh():
    m = to_manifold(lid_blank()) - thread_solid(FEMALE_CREST, LID_FLOOR_TOP, LID_RIM_Z - LID_FLOOR_TOP + 0.1)
    return m - to_manifold(female_chamfer(LID_RIM_Z).union(scallops()).union(lid_center_cuts()))

def coupon_thread_body_mesh():
    ring = revolve([(BORE_R, SHOULDER_Z), (BODY_R - 0.4, SHOULDER_Z), (BODY_R, SHOULDER_Z + 0.4), (BODY_R, SHOULDER_Z + 1.5), (BORE_R, SHOULDER_Z + 1.5)])
    m = to_manifold(ring) + thread_solid(MALE_ROOT, -BODY_H, SHOULDER_Z + BODY_H + 0.05)
    return m - to_manifold(male_chamfer().union(cyl(BORE_R, -BODY_H - 1, 10)))

def coupon_thread_lid_mesh():
    ring = revolve([(BORE_R, LID_FLOOR_TOP - 1.5), (BODY_R, LID_FLOOR_TOP - 1.5), (BODY_R, LID_RIM_Z - 0.4), (BODY_R - 0.4, LID_RIM_Z), (BORE_R, LID_RIM_Z)])
    m = to_manifold(ring) - thread_solid(FEMALE_CREST, LID_FLOOR_TOP, LID_RIM_Z - LID_FLOOR_TOP + 0.1)
    return m - to_manifold(female_chamfer(LID_RIM_Z).union(cyl(BORE_R, LID_FLOOR_TOP - 2, 10)))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    b = body_mesh(); l = lid_mesh()
    print("thread mesh error, body: %.3f mm" % thread_error(b, MALE_ROOT, -13.0, -8.6))
    print("thread mesh error, lid:  %.3f mm" % thread_error(l, FEMALE_CREST, -14.4, -10.3))
    print("body/lid overlap: %.4f mm3" % (b ^ l).volume())
    for name, m, flip in (("01_body", b, True), ("04_lid", l, False),
                          ("coupon_thread_body", coupon_thread_body_mesh(), True),
                          ("coupon_thread_lid", coupon_thread_lid_mesh(), False)):
        t = save(m, os.path.join(OUT, f"{name}.stl"), flip)
        print(f"{name}: {t.extents.round(2)} watertight={t.is_watertight}")
    for name, fn in (("03_hex_plug", plug), ("05_test_reel", reel), ("coupon_hub", coupon_hub), ("gasket_template", gasket_template)):
        obj = place_on_bed(fn())
        p = os.path.join(OUT, f"{name}.stl")
        cq.exporters.export(obj, p, tolerance=0.01, angularTolerance=0.05)
        t = trimesh.load(p)
        print(f"{name}: {t.extents.round(2)} watertight={t.is_watertight}")
