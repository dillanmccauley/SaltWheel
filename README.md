# Yoyito Hand Line Mount v1 (Rev F): print files

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
| stl/gasket_template.stl | flat | 1 |

`step/` has the same parts for editing in CAD. `source/` has the scripts that generate everything
(Python 3 with `cadquery`, `manifold3d` and `trimesh`). After you measure a real Yoyito, change
`REEL_HEX_AF` (hex hole across flats) and `REEL_HUB_LEN` (hex hole length) in `build_parts.py`, then run
`python3 build_parts.py out` and `python3 make_stl.py out`.

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
- Plug only: 4 mm brim, since it is tall for its footprint. Its front flange underside is a short overhang; sand it flat if it droops.
- Body only: fuzzy skin on outside walls, 0.2 mm thick, 0.6 mm point distance, for wet grip

## Order of work

1. Dry the PETG (65 °C, 4–6 h). Clean and level the bed. Use PEI, or glass with a thin layer of glue stick.
2. Plate 1: both thread coupons, the hub coupon and one plug (about 2 h).
   - The male and female thread rings should screw together by hand in under one turn, snug, with no wobble.
   - The M8 nylon nut should press into the hub coupon; the Ø8 rod should pass through its hole.
3. Fix anything that failed and reprint that coupon.
   - Threads tight: XY size compensation −0.05 mm on both thread parts. Loose or wobbly: +0.05 mm.
   - Pin hole tight: drill it out with an 8.2 mm drill.
4. Plate 2: body. Plate 3: lid. Plate 4: test reel and two spare plugs.
5. Clean up: remove strings, run a fingernail through the threads, ream each plug bore with an 8.5 mm
   drill by hand, sand the reel's front wall and lip with 400 grit, and clear the tie hole with a 2.5 mm drill.
6. Make the pin from Ø8 Delrin rod: cut it a little long, face it to 56.35 mm, chamfer both ends 0.5 mm.
   Cut 10 mm of M8 × 1.25 thread on one end with the die, keeping it square. Spin the rod in a drill and
   file a 45° V groove centered 54.25 mm from the threaded end, down to a 7.0 mm root.
7. Lay the gasket template on 1 mm silicone sheet and cut along both edges with a sharp hobby knife
   (gasket 74.2 ID × 79.0 OD).
8. Assemble:
   1. Press the nylon nut into the hex pocket inside the body's hub.
   2. Thread the pin in from the top until it stands 42.35 mm above the top face.
   3. Drop the PTFE washer over the pin.
   4. Push a plug into the reel from the front, tab end first, until the barbs click behind the back face.
      The reel is now captured between the barbs and the plug's front flange. (To remove the plug later,
      off the pin: squeeze the barbs in from the back and push it out the front.)
   5. Push the reel onto the pin until it clicks. It should spin freely and pull off with a firm tug, taking the plug with it.
   6. Slip the gasket over the body's male thread onto the shoulder, then screw the lid on hand tight.

Rough totals: about 140 g of PETG and 13–15 h of printing.

## Buy

- PETG filament, 1.75 mm, about 250 g
- Delrin (acetal) rod, Ø8 mm, 60 mm piece
- M8 × 1.25 hand die and holder
- M8 nylon hex nut (13 mm across flats)
- PTFE washer, 8.4 ID × 18 OD × 1 mm
- Silicone sheet, 1.0 mm, 50A–60A
- Drills: 2.5, 8.2 and 8.5 mm (or 21/64 and 11/32 in)
- A fingerless glove for palming the rim

After saltwater trips, pull the reel off, unscrew the lid, rinse everything in warm fresh water, and let it
dry apart. Don't oil or grease it; grease holds sand.
