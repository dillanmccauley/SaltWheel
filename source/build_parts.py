"""Yoyito hand line mount v1 - parametric part models (CadQuery).

Run:  python3 build_parts.py <outdir>
Writes print-oriented STL and STEP files for every printable part.
All dimensions in mm. Assembly frame: body top face at z = 0, z up.
"""
import math, os, sys
import cadquery as cq

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)

# ---------------- shared parameters ----------------
BODY_R = 40.0            # body radius
BODY_H = 14.0            # body height (top face z=0, bottom z=-14)
TOP_PLATE = 3.0
HUB_R = 12.0             # hub radius; its bottom face is the center-gasket sealing land
BORE_R = 33.2            # cavity bore, full depth
SHOULDER_Z = -8.3        # body shoulder: gasket seat; male thread below it
PITCH, LEAD, DEPTH = 3.0, 6.0, 1.4   # 2-start: lead = 2 x pitch
MALE_ROOT = 35.6         # body external thread: root r 35.6, crest r 37.0
FEMALE_CREST = 35.85     # lid internal thread: crest r 35.85, root r 37.25 (0.25 clearance)
Z0 = -14.0               # thread phase origin (shared by body and lid so they mate)
PIN_HOLE_R = 4.1
NUT_AF, NUT_DEPTH = 13.2, 6.6
DIV_T = 1.8
DIV_ANGLES = (90, 190, 290)
DIV_BOTTOM = -14.2       # dividers stand 0.2 past the bottom face
GASKET = 0.75            # compressed gasket thickness, between shoulder and lid rim
LID_RIM_Z = SHOULDER_Z - GASKET   # top of the lid skirt (-9.05)
LID_FLOOR_TOP = -14.6    # 0.4 below the divider tips
LID_FLOOR_T = 3.0

# drainage (top face, under the reel). The top face stays flat so the body still prints face down;
# a gutter ring around the washer seat feeds radial grooves whose floors slope down to the rim.
GUTTER_R0, GUTTER_R1, GUTTER_DEPTH = 9.6, 11.4, 0.8   # R0 = plug pocket radius
DRAIN_GROOVES, DRAIN_W, DRAIN_DEPTH_RIM, DRAIN_ANGLE0 = 6, 3.0, 1.3, 30.0

# pin drain (pin hole -> nut pocket -> out through the lid, sealed off from the compartment)
CG_ID, CG_OD = 17.4, 22.6         # center gasket, cut from the same 1 mm silicone sheet
CG_RECESS_R = CG_OD / 2 + 0.3     # locating recess in the lid floor
CG_RECESS_FLOOR = LID_FLOOR_TOP - 0.5
HUB_BOTTOM = CG_RECESS_FLOOR + GASKET   # hub land compresses the center gasket to the same 0.75 as the rim gasket
LID_DRAIN_R = 5.0                 # through hole in the lid floor, inside the center gasket

# reel-to-body gap: the washer and the plug's foot/barbs sit down in a pocket in the top face, so
# the reel's back face runs REEL_GAP above the body and loose line can't wedge between them.
REEL_GAP = 0.6
PLUG_BACK = 4.0                   # plug: tab ends to reel back face
WASHER_T, WASHER_OD = 1.6, 16.0   # PTFE washer, standard M8 DIN 125: 8.4 x 16 x 1.6
POCKET_R = GUTTER_R0              # set by the plug barbs (corners r 8.1); the 16 mm washer fits inside
POCKET_FLOOR = REEL_GAP - PLUG_BACK - WASHER_T   # washer seat (-5.0)
# water in the pocket drains down three slots past the nut corners to the hub bottom, inside the
# center gasket, and out the lid drain hole
NUT_DRAIN_R0, NUT_DRAIN_R1, NUT_DRAIN_W = 6.8, 8.1, 1.4

# reel interface (from the reel; change these after measuring a real Yoyito)
REEL_HEX_AF = 12.7
REEL_HUB_LEN = 8.0        # test reel: hex runs from the back face to the flat front floor

def tri(u):
    u = u % 1.0
    return 1 - abs(2 * u - 1)

def tri_soft(u, w=0.035, k=9):
    """Triangle wave with crest and root rounded over +/- w (fraction of a pitch), so the
    periodic spline through it does not ripple. Flanks stay at 45 degrees."""
    return sum(tri(u + w * (2 * j / (k - 1) - 1)) for j in range(k)) / k

def thread_curve(base, z_start, n=240):
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = base + DEPTH * tri_soft((z_start - Z0 - LEAD * th / (2 * math.pi)) / PITCH)
        pts.append((r * math.cos(th), r * math.sin(th)))
    return pts

def twisted(base, z_start, h):
    """Solid bounded by the thread surface r(theta, z), from z_start to z_start + h."""
    wp = cq.Workplane("XY", origin=(0, 0, z_start)).spline(thread_curve(base, z_start), periodic=True).close()
    return wp.twistExtrude(h, 360.0 * h / LEAD)

def revolve(profile):
    return cq.Workplane("XZ").polyline(profile).close().revolve(360, (0, 0, 0), (0, 1, 0))

def hex_prism(af, z0, h, rot=0.0):
    d = af / math.cos(math.radians(30))
    return cq.Workplane("XY", origin=(0, 0, z0)).transformed(rotate=(0, 0, rot)).polygon(6, d).extrude(h)

def cyl(r, z0, h, x=0.0, y=0.0):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(r).extrude(h)

def fillet_pts(a, v, b, r, n=6):
    """Points replacing corner v (between a-v and v-b) with an arc of radius r."""
    ax, ay = a[0] - v[0], a[1] - v[1]; bx, by = b[0] - v[0], b[1] - v[1]
    la, lb = math.hypot(ax, ay), math.hypot(bx, by)
    ax, ay, bx, by = ax / la, ay / la, bx / lb, by / lb
    ang = math.acos(max(-1, min(1, ax * bx + ay * by)))
    t = r / math.tan(ang / 2)
    p1 = (v[0] + ax * t, v[1] + ay * t); p2 = (v[0] + bx * t, v[1] + by * t)
    bisx, bisy = ax + bx, ay + by; lbis = math.hypot(bisx, bisy)
    c = (v[0] + bisx / lbis * r / math.sin(ang / 2), v[1] + bisy / lbis * r / math.sin(ang / 2))
    a1 = math.atan2(p1[1] - c[1], p1[0] - c[0]); a2 = math.atan2(p2[1] - c[1], p2[0] - c[0])
    da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    return [(c[0] + r * math.cos(a1 + da * k / n), c[1] + r * math.sin(a1 + da * k / n)) for k in range(n + 1)]

def lug_solid():
    """Lanyard lug above the shoulder, with a 45 deg ramp on top so it prints without
    support when the body is printed top face down. It sits outside the lid's diameter."""
    plan = (cq.Workplane("XY", origin=(0, 0, SHOULDER_Z)).moveTo(38.0, -4.0).lineTo(42.0, -4.0)
            .threePointArc((46.0, 0), (42.0, 4.0)).lineTo(38.0, 4.0).close().extrude(-SHOULDER_Z - 1.3))
    ramp = revolve([(37.0, SHOULDER_Z), (46.5, SHOULDER_Z), (46.5, SHOULDER_Z + 0.5), (40.0, -1.3), (37.0, -1.3)])
    return plan.intersect(ramp)

def male_chamfer():
    """30 deg lead-in on the male thread at the bottom face."""
    return revolve([(MALE_ROOT, -BODY_H - 0.01), (38.5, -BODY_H - 0.01), (38.5, -BODY_H + (38.5 - MALE_ROOT) * 0.577)])

def female_chamfer(z_rim):
    """30 deg lead-in on the female thread at the lid rim."""
    return revolve([(34.0, z_rim + 0.01), (37.6, z_rim + 0.01), (34.0, z_rim - (37.6 - 34.0) * 0.577)])

# ---------------- 01 body ----------------
def body_shell():
    upper = revolve([(0, 0), (BODY_R - 1.2, 0), (BODY_R, -1.2), (BODY_R, SHOULDER_Z + 0.4), (BODY_R - 0.4, SHOULDER_Z), (0, SHOULDER_Z)])
    return upper

def body_extras():
    e = cyl(HUB_R, HUB_BOTTOM, -HUB_BOTTOM - TOP_PLATE + 0.2)
    for a in DIV_ANGLES:
        d = cq.Workplane("XY").box(BORE_R + 0.6 - (HUB_R - 0.5), DIV_T, -TOP_PLATE - DIV_BOTTOM + 0.1, centered=(False, True, False)) \
            .translate((HUB_R - 0.5, 0, DIV_BOTTOM)).rotate((0, 0, 0), (0, 0, 1), a)
        e = e.union(d)
    return e.union(lug_solid())

def drain_cuts():
    """Gutter ring around the washer seat plus radial grooves out to the rim, in the top face."""
    c = revolve([(GUTTER_R0, 0.01), (GUTTER_R1, 0.01), (GUTTER_R1, -GUTTER_DEPTH), (GUTTER_R0, -GUTTER_DEPTH)])
    for k in range(DRAIN_GROOVES):
        g = (cq.Workplane("XZ").polyline([(GUTTER_R0 + 0.5, 0.01), (BODY_R + 1, 0.01), (BODY_R + 1, -DRAIN_DEPTH_RIM),
                                           (GUTTER_R0 + 0.5, -GUTTER_DEPTH)]).close()
             .extrude(DRAIN_W / 2, both=True).rotate((0, 0, 0), (0, 0, 1), DRAIN_ANGLE0 + 360.0 * k / DRAIN_GROOVES))
        c = c.union(g)
    return c

def pocket_cuts():
    c = cyl(POCKET_R, POCKET_FLOOR, -POCKET_FLOOR + 1)
    for a in (0, 120, 240):            # hex_prism puts corners at 0, 60, ...
        s = cq.Workplane("XY").box(NUT_DRAIN_R1 - NUT_DRAIN_R0, NUT_DRAIN_W, POCKET_FLOOR - HUB_BOTTOM + 1.1,
                                   centered=(False, True, False)).translate((NUT_DRAIN_R0, 0, HUB_BOTTOM - 1))
        c = c.union(s.rotate((0, 0, 0), (0, 0, 1), a))
    return c

def body_cuts():
    nut_top = -BODY_H + NUT_DEPTH
    return pocket_cuts().union(hex_prism(NUT_AF, HUB_BOTTOM - 1, nut_top - HUB_BOTTOM + 1).union(cyl(PIN_HOLE_R, HUB_BOTTOM - 1, -HUB_BOTTOM + 2))
            .union(cyl(1.75, SHOULDER_Z - 1, 9, x=42.0)).union(drain_cuts()))

def cavity():
    return revolve([(HUB_R - 0.5, -TOP_PLATE), (BORE_R, -TOP_PLATE), (BORE_R, -BODY_H - 1), (HUB_R - 0.5, -BODY_H - 1)])

def body():
    b = body_shell().union(twisted(MALE_ROOT, -BODY_H, SHOULDER_Z + BODY_H + 0.05))
    b = b.cut(male_chamfer()).cut(cavity())
    b = b.union(body_extras()).cut(body_cuts())
    return b

# ---------------- 04 lid (cap with internal thread) ----------------
def lid_blank():
    zb = LID_FLOOR_TOP - LID_FLOOR_T
    return revolve([(0, zb), (BODY_R - 1.2, zb), (BODY_R, zb + 1.2), (BODY_R, LID_RIM_Z - 0.4), (BODY_R - 0.4, LID_RIM_Z), (0, LID_RIM_Z)])

def scallops():
    zb = LID_FLOOR_TOP - LID_FLOOR_T
    c = None
    for k in range(24):
        a = 2 * math.pi * (k + 0.5) / 24     # offset from the revolve seam at 0 deg
        s = cyl(3.0, zb - 1, LID_RIM_Z - zb + 2, x=42.4 * math.cos(a), y=42.4 * math.sin(a))
        c = s if c is None else c.union(s)
    return c

def lid_center_cuts():
    """Center-gasket recess under the hub and the pin drain hole through the floor."""
    zb = LID_FLOOR_TOP - LID_FLOOR_T
    return cyl(CG_RECESS_R, CG_RECESS_FLOOR, 1.0).union(cyl(LID_DRAIN_R, zb - 1, LID_FLOOR_T + 2))

def lid():
    l = lid_blank().cut(twisted(FEMALE_CREST, LID_FLOOR_TOP, LID_RIM_Z - LID_FLOOR_TOP + 0.1))
    return l.cut(female_chamfer(LID_RIM_Z)).cut(scallops()).cut(lid_center_cuts())

# ---------------- 03 hex plug (local: tab ends z=0, which sit on the washer) ----------------
# The reel is captured between barbs behind its back face and a flange on its front face.
#   - pulling the reel off, or line pulling forward: reel front face -> flange -> neck snap
#   - pressing the reel toward the body: reel back face -> square barb shoulders -> tab ends -> washer
# The six tabs flex inward only while the plug is pushed through the reel's hex hole. The bore is
# relieved to r 4.45 along the tabs (thinner, more flexible tabs), so on the pin they can move inward
# 0.45 at most, less than the 0.75 barb overlap, and the reel stays captured.
PLUG_GAP = 0.05                  # axial clearance at each reel face
BARB_AF = REEL_HEX_AF - 0.15 + 1.5    # barb flats stand 0.75 proud of the hex flats
FOOT_AF = 11.2
FRONT_FLANGE_R, FRONT_FLANGE_T = 9.0, 2.5
NECK_LEN = 11.0
TAB_RELIEF_R = 4.45             # bore radius along the tabs (pin clearance bore is 4.3)
LAND_R = 4.1                    # anti-wobble bearing bands on the pin: ream to 8.2
LAND_BOTTOM_LEN = 2.0           # at the tab tips
LAND_TOP_BELOW_NECK = (7.5, 2.2) # top band spans neck_top-7.5 .. neck_top-2.2, just under the snap bead
PIN_STANDOUT_ABOVE_PLUG = 1.3   # pin tip above the plug neck top

def plug_z():
    back = PLUG_BACK                    # reel back face (local)
    front = back + REEL_HUB_LEN         # reel front face
    flange_bot = front + PLUG_GAP
    neck_bot = flange_bot + FRONT_FLANGE_T
    return back, front, flange_bot, neck_bot, neck_bot + NECK_LEN

def plug():
    af = REEL_HEX_AF - 0.15
    back, front, flange_bot, neck_bot, neck_top = plug_z()
    barb_top = back - PLUG_GAP
    tab_slot_top = min(14.0, flange_bot - 1.5)   # tabs flex up to here; stays below the front flange
    p = hex_prism(FOOT_AF, 0, 1.25)
    p = p.union(cq.Workplane("XY", origin=(0, 0, 1.2)).polygon(6, FOOT_AF / math.cos(math.radians(30)))
                .workplane(offset=barb_top - 1.0 - 1.2).polygon(6, BARB_AF / math.cos(math.radians(30))).loft())
    p = p.union(hex_prism(BARB_AF, barb_top - 1.0, 1.0))
    p = p.union(hex_prism(af, barb_top - 0.01, flange_bot - barb_top + 0.11))
    rib_len = flange_bot - tab_slot_top - 3.5    # anti-rattle ribs, only where a long hex leaves room
    for a in ((30, 150, 270) if rib_len > 1.0 else ()):
        rib = cq.Workplane("XY").box(0.35, 1.0, rib_len, centered=(False, True, False)) \
            .translate((af / 2 - 0.1, 0, tab_slot_top + 2.0)).rotate((0, 0, 0), (0, 0, 1), a)
        p = p.union(rib)
    p = p.union(revolve([(0, flange_bot), (FRONT_FLANGE_R, flange_bot), (FRONT_FLANGE_R, neck_bot - 0.5),
                         (FRONT_FLANGE_R - 0.5, neck_bot), (0, neck_bot)]))
    p = p.union(cyl(5.5, neck_bot - 0.1, NECK_LEN + 0.1))
    p = p.cut(cyl(4.3, -1, neck_top + 2)).cut(cyl(TAB_RELIEF_R, LAND_BOTTOM_LEN, tab_slot_top - LAND_BOTTOM_LEN))
    lo, hi = LAND_TOP_BELOW_NECK
    p = p.union(cyl(4.31, 0, LAND_BOTTOM_LEN).cut(cyl(LAND_R, -1, 5)))           # bottom band
    p = p.union(cyl(4.31, neck_top - lo, lo - hi).cut(cyl(LAND_R, -30, 80)))    # top band
    p = p.union(revolve([(4.35, neck_top - 2.1), (3.6, neck_top - 0.9), (3.6, neck_top - 0.7), (4.35, neck_top)]))
    slot_bottom = neck_top - 5.5
    for a in (45, 135, 225, 315):
        s = cq.Workplane("XY").box(4.0, 1.2, 6.0, centered=(False, True, False)).translate((3.0, 0, slot_bottom + 0.6))
        s = s.union(cq.Workplane("YZ", origin=(3.0, 0, slot_bottom + 0.6)).circle(0.6).extrude(4.0))
        p = p.cut(s.rotate((0, 0, 0), (0, 0, 1), a))
    for a in range(0, 360, 60):          # tab slots at the hex corners, round top end
        s = cq.Workplane("XY").box(5.0, 1.0, tab_slot_top + 1.0, centered=(False, True, False)).translate((3.5, 0, -1.0))
        s = s.union(cq.Workplane("YZ", origin=(3.5, 0, tab_slot_top)).circle(0.5).extrude(5.0))
        p = p.cut(s.rotate((0, 0, 0), (0, 0, 1), a))
    return p

def pin_dims():
    """Delrin pin: (height above the body's top face, total length, groove center from the threaded end)."""
    stand = POCKET_FLOOR + WASHER_T + plug_z()[4] + PIN_STANDOUT_ABOVE_PLUG
    length = stand + BODY_H
    return stand, length, length - 2.1

# ---------------- 05 test reel (local: back face z=0) ----------------
# Yoyito-style spool: line groove at the back, cone that the line slides off, and a recessed front
# face: a flat floor through which the finger holes pass, tapering up to the front rim, around a
# central hex hole that ends flush with the floor; the plug's flange and neck sit inside the recess. The core root (REEL_V) is raised to trade line capacity for a deep, flat floor.
REEL_A = (44.45, 3.0); REEL_V = (33.0, 6.1); REEL_L = (42.0, 25.4)
REEL_FRONT = REEL_L[1]
DISH_FLOOR_Z = REEL_HUB_LEN           # flat floor, flush with the end of the hex; = finger-hole length
DISH_FLAT_R = 29.5                    # flat floor out to here, then a straight taper...
DISH_R = 38.5                         # ...up to this radius at the front face
DISH_FILLET, DISH_RIM_FILLET = 3.0, 2.0
FINGER_HOLES, FINGER_D, FINGER_PCR = 6, 17.0, 19.5
FINGER_ANGLE0 = 30.0                  # one hole lines up with the line-tie hole

def reel_profile():
    pts = [(0, 0)]
    pts += fillet_pts((0, 0), (44.45, 0), (44.45, 3.0), 1.0)
    pts += fillet_pts((44.45, 0), REEL_A, REEL_V, 0.6, 3)
    pts += fillet_pts(REEL_A, REEL_V, REEL_L, 1.5)
    pts += fillet_pts(REEL_V, REEL_L, (0, REEL_FRONT), 1.5)
    pts += [(0, REEL_FRONT)]
    return pts

def dish_cut():
    """Flat floor from the hub boss to DISH_FLAT_R, straight taper to DISH_R at the front face,
    both bends rounded."""
    f, z = (DISH_FLAT_R, DISH_FLOOR_Z), (DISH_R, REEL_FRONT)
    pts = [(0, REEL_FRONT + 1), (0, DISH_FLOOR_Z)]
    pts += fillet_pts((0, DISH_FLOOR_Z), f, z, DISH_FILLET)
    rim = fillet_pts(f, z, (DISH_R + 10, REEL_FRONT), DISH_RIM_FILLET)
    pts += rim[:-1] + [(rim[-1][0], REEL_FRONT + 1)]
    return revolve(pts)

def reel():
    r = revolve(reel_profile())
    r = r.cut(dish_cut())
    r = r.cut(hex_prism(REEL_HEX_AF, -1, REEL_FRONT + 3))
    h2 = REEL_HEX_AF / 2
    r = r.cut(revolve([(0, REEL_HUB_LEN + 0.01), (h2 + 0.6, REEL_HUB_LEN + 0.01), (h2 - 0.01, REEL_HUB_LEN - 0.6), (0, REEL_HUB_LEN - 0.6)]))
    for k in range(FINGER_HOLES):
        a = math.radians(FINGER_ANGLE0 + 360.0 * k / FINGER_HOLES)
        r = r.cut(cyl(FINGER_D / 2, -1, REEL_FRONT + 3, x=FINGER_PCR * math.cos(a), y=FINGER_PCR * math.sin(a)))
    tie = (cq.Workplane("YZ", origin=(FINGER_PCR, 0, REEL_V[1] + 0.5)).circle(1.25).extrude(REEL_V[0] + 4.0 - FINGER_PCR)
           .rotate((0, 0, 0), (0, 0, 1), FINGER_ANGLE0))
    return r.cut(tie)

# ---------------- coupons and template ----------------
def coupon_hub():
    c = cyl(15.0, 0, 10.0)
    c = c.cut(cyl(PIN_HOLE_R, -1, 12)).cut(hex_prism(NUT_AF, 10.0 - NUT_DEPTH, NUT_DEPTH + 1))
    return c

def coupon_thread_body():
    """Male thread ring with a short shoulder flange, like the bottom of the body."""
    c = revolve([(BORE_R, SHOULDER_Z), (BODY_R - 0.4, SHOULDER_Z), (BODY_R, SHOULDER_Z + 0.4), (BODY_R, SHOULDER_Z + 1.5), (BORE_R, SHOULDER_Z + 1.5)])
    c = c.union(twisted(MALE_ROOT, -BODY_H, SHOULDER_Z + BODY_H + 0.05))
    return c.cut(male_chamfer()).cut(cyl(BORE_R, -BODY_H - 1, 10))

def coupon_thread_lid():
    """Female thread ring with a 1.5 floor ring, like the lid."""
    c = revolve([(BORE_R, LID_FLOOR_TOP - 1.5), (BODY_R, LID_FLOOR_TOP - 1.5), (BODY_R, LID_RIM_Z - 0.4), (BODY_R - 0.4, LID_RIM_Z), (BORE_R, LID_RIM_Z)])
    c = c.cut(twisted(FEMALE_CREST, LID_FLOOR_TOP, LID_RIM_Z - LID_FLOOR_TOP + 0.1))
    return c.cut(female_chamfer(LID_RIM_Z)).cut(cyl(BORE_R, LID_FLOOR_TOP - 2, 10))

def gasket_template():
    """Rim gasket ring (outer) and center gasket ring (inner, concentric); cut along both edges of each."""
    g = cyl(39.5, 0, 1.6).cut(cyl(37.1, -1, 4))
    g = g.union(cq.Workplane("XY").box(6, 8, 1.6, centered=(True, False, False)).translate((0, 38.8, 0)))
    return g.union(cyl(CG_OD / 2, 0, 1.6).cut(cyl(CG_ID / 2, -1, 4)))

# ---------------- export ----------------
def place_on_bed(obj, flip=False):
    if flip:
        obj = obj.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = obj.val().BoundingBox()
    return obj.translate((0, 0, -bb.zmin))

PARTS = {
    "01_body":              (body, True),
    "03_hex_plug":          (plug, False),
    "04_lid":               (lid, False),
    "05_test_reel":         (reel, False),
    "coupon_hub":           (coupon_hub, False),
    "coupon_thread_body":   (coupon_thread_body, True),
    "coupon_thread_lid":    (coupon_thread_lid, False),
    "gasket_template":      (gasket_template, False),
}

if __name__ == "__main__":
    only = sys.argv[2:] or list(PARTS)
    for name in only:
        fn, flip = PARTS[name]
        obj = fn()
        bed = place_on_bed(obj, flip)
        cq.exporters.export(bed, os.path.join(OUT, f"{name}.stl"), tolerance=0.02, angularTolerance=0.1)
        cq.exporters.export(bed, os.path.join(OUT, f"{name}.step"))
        bb = bed.val().BoundingBox()
        print(f"{name}: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm, valid={bed.val().isValid()}", flush=True)
    print("pin: %.2f above top face, %.2f long, groove %.2f from threaded end" % pin_dims())
