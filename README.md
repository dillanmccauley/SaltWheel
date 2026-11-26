# Yoyito Hand Line Mount v1 (Rev G): print files

All files are in millimeters and already oriented for printing. Don't rotate them in the slicer.

| File | Print as | Qty |
|---|---|---|
| stl/01_body.stl | top face down, dividers and male thread pointing up | 1 |
| stl/03_hex_plug.stl | tab end down, 4 mm brim | 3 (2 spares) |
| stl/04_lid.stl | outer face down, open side up | 1 |
| stl/05_test_reel.stl | back face down | 1 |
| stl/coupon_hub.stl | as loaded | 1 |
| stl/coupon_thread_body.stl | as loaded | 1 |
| stl/coupon_thread_lid.stl | as loaded | 1 |
| stl/gasket_template.stl | flat (two rings: rim gasket and center gasket) | 1 |

`step/` has the same parts for editing in CAD. `source/` has the scripts that generate everything
(Python 3 with `cadquery`, `manifold3d` and `trimesh`). After you measure a real Yoyito, change
`REEL_HEX_AF` (hex hole across flats) and `REEL_HUB_LEN` (hex hole length) in `build_parts.py`, then run
`python3 build_parts.py out` and `python3 make_stl.py out`. The plug and test reel follow those values, and
`build_parts.py` prints the matching pin length, stand-out and groove position for step 6 below.

## Drainage and sealing (new in Rev G)

- **Reel close to the body:** the washer and the plug's foot sit down in a 19.2 mm pocket in the body's top
  face, so the reel's back face runs only 0.6 mm above the body (`REEL_GAP`). Line that slips off the back of
  the reel during a retrieve can't wedge between them. The plug rides the pin on two short 8.2 mm bearing bands
  about 20 mm apart, so the reel can tilt at most about 0.4 mm at the body's edge and doesn't rub.
- **Under the reel:** a gutter ring around the pocket feeds six radial grooves that get deeper toward the rim,
  so water and sand under the reel run out the edge. Water in the pocket drains down three slots past the
  nut corners and out the lid (below). The face is still flat, so the body prints top face down as before.
- **Down the pin:** water that follows the pin thread into the nut pocket no longer reaches the tackle
  compartment. The hub's bottom face now presses a small silicone center gasket into a recess in the lid
  floor, and a 10 mm hole in the lid floor (inside that gasket) lets that water drain straight out the back.
  The compartment is sealed by the rim gasket and the center gasket together. Both are cut from 2 mm silicone
  sheet and squeeze 20% (2.0 → 1.6 mm) when the lid is hand tight (`GASKET_T`, `GASKET_SQUEEZE`). To make
  room without losing thread, the body's male thread runs 0.85 mm below its bottom face and the lid is 0.85 mm
  deeper, so the thread engagement is the same as before.
- **Test reel:** the front face is recessed like a real Yoyito: a flat floor 8 mm above the back face, tapering
  up to the front rim, with six 17 mm finger holes through the floor around the hex hole. The hex ends flush with
  the floor (8 mm long), and the plug's flange and neck sit down inside the recess. The holes are only 8 mm
  long, so fingers pass straight through, and they also let the reel drain. To make room, the line core is larger
  (root diameter 66 mm instead of 57), so the groove is shallower and holds less line than Rev F.

## Slicer settings (PETG, Ender 3 Pro)

- Nozzle 235–240 °C (240 for the first layer), bed 75–80 °C
- Layer height 0.20 for the body and plug; 0.16 for the lid, thread coupons and test reel
- Speed 40–50 mm/s, outer walls 25 mm/s, first layer 20 mm/s
- Fan off for the first 3 layers, then 30–50%
- Retraction 5–6 mm at 40 mm/s (Bowden)
- Elephant foot compensation 0.15–0.2 mm (Cura: Initial Layer Horizontal Expansion −0.15)
- Seam random or back
- Supports off. Add a 3 mm brim only if an edge lifts.
- Walls / infill: body 4 / 30%, lid 4 / 30%, plug 4 / 40%, test reel 5 / 30%, coupons 4 / 30%
- Plug only: 4 mm brim, since it is tall for its footprint. With the 8 mm hex its snap tabs are shorter and about
  1.5× stiffer than Rev F's; if pushing it through the reel takes more than a firm thumb press, try one plug with
  XY size compensation −0.05 mm. Its front flange underside is a short overhang; sand it flat if it droops.
- Body only: fuzzy skin on outside walls, 0.2 mm thick, 0.6 mm point distance, for wet grip

## Order of work

1. Dry the PETG (65 °C, 4–6 h). Clean and level the bed. Use PEI, or glass with a thin layer of glue stick.
2. Plate 1: both thread coupons, the hub coupon and one plug (about 2 h).
   - The male and female thread rings should screw together by hand in under one turn, snug, with no wobble.
   - The M8 nylon nut should press into the hub coupon; the Ø8 rod should pass through its hole.
3. Fix anything that failed and reprint that coupon.
   - Threads tight: XY size compensation −0.05 mm on both thread parts. Loose or wobbly: +0.05 mm.
   - Pin hole tight: drill it out with an 8.2 mm drill. The pin should slide through with no side play;
     that is the fit the plug's bearing bands need.
4. Plate 2: body. Plate 3: lid. Plate 4: test reel and two spare plugs.
5. Clean up: remove strings, run a fingernail through the threads, ream each plug bore by hand with an 8.2 mm
   drill from the tab end to a depth of 23 mm (tape-mark the drill so you don't cut the snap bead at the top), sand the reel's front lip, the taper and the finger-hole edges with 400 grit, clear the tie hole
   with a 2.5 mm drill, and check that the drain grooves, the pocket's three drain slots and the lid's center drain hole are clear.
   The pocket floor prints as a bridge; if it sags, sand it flat so the washer sits level.
6. Make the pin from Ø8 Delrin rod: cut it a little long, face it to 37.45 mm, chamfer both ends 0.5 mm.
   Cut 10 mm of M8 × 1.25 thread on one end with the die, keeping it square. Spin the rod in a drill and
   file a 45° V groove centered 35.35 mm from the threaded end, down to a 7.0 mm root.
7. Lay the gasket template on 2 mm silicone sheet and cut along both edges of both rings with a sharp
   hobby knife (rim gasket 74.2 ID × 79.0 OD, center gasket 17.4 ID × 22.6 OD). Hold the knife vertical
   and cut in two or three light passes; 2 mm sheet pulls if you force one deep cut.
8. Assemble:
   1. Press the nylon nut into the hex pocket inside the body's hub.
   2. Thread the pin in from the top until it stands 23.45 mm above the top face.
   3. Drop the PTFE washer over the pin into the pocket.
   4. Push a plug into the reel from the front, tab end first, until the barbs click behind the back face.
      The reel is now captured between the barbs and the plug's front flange. (To remove the plug later,
      off the pin: squeeze the barbs in from the back and push it out the front.)
   5. Push the reel onto the pin until it clicks. It should spin freely and pull off with a firm tug, taking the plug with it.
   6. Slip the rim gasket over the body's male thread onto the shoulder and drop the center gasket into the
      round recess in the middle of the lid floor, then screw the lid on hand tight.

Rough totals: about 140 g of PETG and 13–15 h of printing.

## Buy

- PETG filament, 1.75 mm, about 250 g
- Delrin (acetal) rod, Ø8 mm, 45 mm piece
- M8 × 1.25 hand die and holder
- M8 nylon hex nut (13 mm across flats)
- PTFE washer, M8 × 16 × 1 mm (8.4 ID × 16 OD × 1 mm)
- Silicone sheet, 2.0 mm, 60A–70A (70A is fine and resists extruding past the thread; firmer sheet just needs a
  firm hand-tight turn on the lid)
- Drills: 2.5, 8.2 and 8.5 mm (or 21/64 and 11/32 in)
- A fingerless glove for palming the rim

After saltwater trips, pour fresh water down along the pin first (it runs out the hole in the lid), then pull
the reel off, unscrew the lid, rinse everything in warm fresh water, and let it dry apart. Don't oil or grease it; grease holds sand.
