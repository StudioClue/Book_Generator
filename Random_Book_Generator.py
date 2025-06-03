import Rhino.Geometry as rg
import random

# === INPUTS ===
bf_crv = bottom_front  # Front bottom edge curve
bb_crv = bottom_back   # Back bottom edge curve
tb_crv = top_back      # Back top curve

# === SETTINGS ===
book_min_w = 20.0
book_max_w = 40.0
book_min_h = 30.0
book_max_h = 36.0
book_min_t = 0.8
book_max_t = 5.0
max_books = 150
tolerance = 0.001

books = []

# === Utility: Create a plane surface perpendicular to bookshelf direction ===
def create_section_surface(origin, normal, size=50.0):
    normal.Unitize()
    x_guess = rg.Vector3d(1, 0, 0) if abs(normal * rg.Vector3d(1, 0, 0)) < 0.99 else rg.Vector3d(0, 1, 0)
    x_axis = rg.Vector3d.CrossProduct(x_guess, normal)
    x_axis.Unitize()
    y_axis = rg.Vector3d.CrossProduct(normal, x_axis)
    return rg.PlaneSurface(rg.Plane(origin, x_axis, y_axis), rg.Interval(-size, size), rg.Interval(-size, size))

# === Initial Section ===
start_pt = bf_crv.PointAtStart
next_pt = bf_crv.PointAt(bf_crv.Domain.T0 + 0.01 * bf_crv.Domain.Length)
initial_normal = next_pt - start_pt
curr_srf = create_section_surface(start_pt, initial_normal)

# === Main Loop ===
for i in range(max_books):
    bf_result = rg.Intersect.Intersection.CurveSurface(bf_crv, curr_srf, tolerance, tolerance)
    bb_result = rg.Intersect.Intersection.CurveSurface(bb_crv, curr_srf, tolerance, tolerance)

    if not (bf_result and bb_result) or bf_result.Count == 0 or bb_result.Count == 0:
        break

    pt_front = bf_result[0].PointA
    pt_back = bb_result[0].PointA
    success, t = tb_crv.ClosestPoint(pt_back)
    if not success:
        break
    pt_top = tb_crv.PointAt(t)

    book_w = random.uniform(book_min_w, book_max_w)
    base_vec = pt_front - pt_back
    base_vec.Unitize()
    pt_scaled = pt_back + base_vec * book_w
    base_line_scaled = rg.Line(pt_back, pt_scaled)

    book_h = random.uniform(book_min_h, book_max_h)
    height_vec = pt_top - pt_back
    height_vec.Unitize()
    height_vec *= book_h

    base_crv = rg.LineCurve(base_line_scaled)
    moved_crv = base_crv.DuplicateCurve()
    moved_crv.Transform(rg.Transform.Translation(height_vec))

    loft = rg.Brep.CreateFromLoft([base_crv, moved_crv], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
    if not loft or len(loft) == 0:
        break
    height_brep = loft[0]

    # Overlap pushback
    if i > 0:
        intersection = rg.Intersect.Intersection.BrepBrep(books[-1], height_brep, tolerance)
        if intersection:
            inter_crvs = intersection[1]
            inter_srfs = intersection[2]
            max_push = 5.0
            step = 0.01
            move_count = 0
            face = height_brep.Faces[0]
            u, v = face.Domain(0).Mid, face.Domain(1).Mid
            normal = face.NormalAt(u, v)
            normal.Unitize()
            while (len(inter_crvs) > 1 or len(inter_srfs) > 0) and move_count * step < max_push:
                xform = rg.Transform.Translation(normal * step)
                height_brep.Transform(xform)
                moved_crv.Transform(xform)
                intersection = rg.Intersect.Intersection.BrepBrep(books[-1], height_brep, tolerance)
                inter_crvs = intersection[1]
                inter_srfs = intersection[2]
                move_count += 1

    face = height_brep.Faces[0]
    book_t = random.uniform(book_min_t, book_max_t)
    book_brep = rg.Brep.CreateFromOffsetFace(face, book_t, tolerance, False, True)
    if not book_brep or book_brep.Faces.Count == 0:
        break

    books.append(book_brep)

    # Update section surface from midpoint of last book face
    face = book_brep.Faces[0]
    u_dom = face.Domain(0)
    v_dom = face.Domain(1)
    u_mid = (u_dom.T0 + u_dom.T1) / 2.0
    v_mid = (v_dom.T0 + v_dom.T1) / 2.0
    origin = face.PointAt(u_mid, v_mid)
    normal = face.NormalAt(u_mid, v_mid)
    curr_srf = create_section_surface(origin, normal)

# === Final Check: Remove last book if it overlaps with second last ===
if len(books) >= 2:
    last = books[-1]
    second_last = books[-2]
    result = rg.Intersect.Intersection.BrepBrep(second_last, last, tolerance)
    if result:
        inter_crvs = result[1]
        inter_srfs = result[2]
        if len(inter_crvs) > 0 or len(inter_srfs) > 0:
            books.pop()

# === OUTPUT ===
a = books
