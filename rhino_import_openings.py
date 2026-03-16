import os
import math

import rhinoscriptsyntax as rs


# Fichier DXF a ouvrir. Laisse None pour choisir le fichier a la main.
try:
    _SCRIPT_DIR = os.path.dirname(__file__)
except NameError:
    _SCRIPT_DIR = os.getcwd()

DXF_PATH = os.path.join(_SCRIPT_DIR, "placement_mask.dxf")

# Nom de la couche a afficher.
OPENINGS_LAYER = "OPENINGS"
EDGE_CUTS_LAYER = "EDGE_CUTS"
HINGE_AXIS_LAYER = "HINGE_AXIS"
JIG_AXIS_LAYER = "JIG_AXIS"
JIG_POSTS_LAYER = "JIG_POSTS"
JIG_PLATE_LAYER = "JIG_PLATE"
JIG_HINGE_CLEARANCE_CUT_LAYER = "JIG_HINGE_CLEARANCE_CUT"
JIG_POCKET_CUT_LAYER = "JIG_POCKET_CUT"
JIG_OPENINGS_CUT_LAYER = "JIG_OPENINGS_CUT"
JIG_RESULT_LAYER = "JIG_RESULT"
HINGE_BODY_LAYER = "HINGE_BODY"
SUPPORT_RESULT_LAYER = "SUPPORT_RESULT"
EJECTION_CUT_LAYER = "EJECTION_CUT"
LEVER_CUT_LAYER = "LEVER_CUT"
PCB_SEAT_CUT_LAYER = "PCB_SEAT_CUT"
JIG_LEVER_LAYER = "JIG_LEVER"
PLATE_LAYER = "PLATE"
PLATE_1_LAYER = "PLATE_1"
PLATE_2_LAYER = "PLATE_2"
PLATE_3_LAYER = "PLATE_3"
MASK_JIG_RESULT_LAYER = "MASK_JIG_RESULT"

# Si True, supprime tout ce qui existe deja dans le document avant import.
CLEAR_DOCUMENT_BEFORE_IMPORT = False

# Si True, masque toutes les couches sauf OPENINGS et EDGE_CUTS.
HIDE_OTHER_LAYERS = True

# Parametres de l'axe de charniere, modifiable si on veut reculer ou avancer la charniere
HINGE_AXIS_OFFSET_FROM_YMIN = -26.0
#HINGE_AXIS_OFFSET_FROM_YMIN = -36.0
HINGE_AXIS_Z = 6.0
HINGE_AXIS_DIAMETER = 4.2
HINGE_AXIS_EXTRA_X_MIN = 10.0
HINGE_AXIS_EXTRA_X_MAX = 10.0
HINGE_AXIS_COLOR = (220, 120, 20)
JIG_AXIS_DIAMETER = 3.0
JIG_AXIS_COLOR = (240, 180, 40)
JIG_POSTS_COLOR = (240, 140, 80)
JIG_PLATE_COLOR = (255, 180, 110)

# Parametres des montants du jig
JIG_POST_ZMIN = 3.0
JIG_POST_ZMAX = 10.0
JIG_POST_BOTTOM_FILLET_RADIUS = 2.0

# Parametres d'encombrement communs par rapport au PCB
PCB_OUTER_OFFSET = 4.0
SUPPORT_OUTER_OVERHANG = 2.0
HINGE_BODY_X_OFFSET_DELTA = -3.0

# Parametres du plateau du jig
JIG_PLATE_ZMIN = 3.0
JIG_PLATE_ZMAX = 5.0
JIG_PLATE_TOP_FILLET_RADIUS = 2.0

# Parametres du corps de charniere
HINGE_BODY_WIDTH_Y = 8.0
HINGE_BODY_HEIGHT_Z = 10.0
HINGE_BODY_FILLET_RADIUS = 2.0
HINGE_BODY_ZMIN = 0.0
HINGE_BODY_COLOR = (120, 120, 220)

# Parametres du plateau
PLATE_1_OFFSET_FROM_AXIS_Y = 10.0
PLATE_1_TOP_FILLET_RADIUS = 4.0
PLATE_1_ZMIN = 0.0
PLATE_1_ZMAX = 5.0

PLATE_2_TOP_FILLET_RADIUS = 2.0
PLATE_2A_ZMIN = 0.0
PLATE_2A_ZMAX = 3.0
PLATE_2B_ZMIN = 3.0
PLATE_2B_ZMAX = 5.0
PLATE_1_COLOR = (80, 180, 200)
PLATE_2_COLOR = (70, 140, 240)
PLATE_3_COLOR = (220, 90, 170)
PLATE_RESULT_LAYER = "PLATE_RESULT"
PLATE_RESULT_COLOR = (40, 200, 120)
SUPPORT_RESULT_COLOR = (40, 160, 90)
EJECTION_CUT_COLOR = (200, 40, 40)
LEVER_CUT_COLOR = (180, 60, 20)
PCB_SEAT_CUT_COLOR = (40, 200, 200)
JIG_LEVER_COLOR = (255, 110, 40)
JIG_HINGE_CLEARANCE_CUT_COLOR = (255, 70, 70)
JIG_POCKET_CUT_COLOR = (180, 20, 120)
JIG_OPENINGS_CUT_COLOR = (120, 20, 180)
JIG_RESULT_COLOR = (255, 210, 90)
MASK_JIG_RESULT_COLOR = (110, 210, 255)

# Ouverture d'ejection du PCB
EJECTION_MARGIN_X = 10.0
EJECTION_MARGIN_Y = 10.0
EJECTION_ZMIN = 0.0
EJECTION_ZMAX = 5.0

# Decoupe pour le levier du jig
LEVER_CUT_SIDE_MARGIN_TOTAL = 12.0
LEVER_CUT_MIN_WIDTH = 4.0
LEVER_CUT_YMAX_EXTRA = 50.0
LEVER_CUT_ZMIN = 3.0
LEVER_CUT_ZMAX = 5.0

# Empreinte PCB dans le support
PCB_SEAT_MARGIN_XY = 0.15
PCB_SEAT_ZMIN = 1.4
PCB_SEAT_ZMAX = 3.0

# Levier du jig
JIG_LEVER_OVERHANG_Y = 3.0
JIG_LEVER_ZMIN = 3.0
JIG_LEVER_ZMAX = 5.0

# Degagement pour eviter le contact avec la charniere
JIG_HINGE_CLEARANCE_DEPTH_Y = 3.0
JIG_HINGE_CLEARANCE_ZMIN = 0.0
JIG_HINGE_CLEARANCE_ZMAX = 5.0

# Poche et decoupe des openings dans le plateau du jig
JIG_BOTTOM_SKIN_THICKNESS = 0.4

# Jig de positionnement du masque de soudure
SOLDER_MASK_BORDER = 10.0
MASK_JIG_OUTER_MARGIN = 5.0
MASK_JIG_OUTER_FILLET_RADIUS = 5.0
MASK_JIG_HEIGHT = 3.0
MASK_JIG_MASK_CLEARANCE_XY = 0.15
MASK_JIG_MASK_POCKET_DEPTH = 0.3
MASK_JIG_PCB_CUT_DEPTH_FROM_TOP = 1.9
MASK_JIG_SMALL_PCB_THRESHOLD = 16.0
MASK_JIG_EJECTION_HOLE_DIAMETER = 10.0
MASK_JIG_EJECTION_HOLE_MIN_SPACING = 3.0
MASK_JIG_GAP_TO_SUPPORT = 10.0

def clear_document():
    ids = rs.AllObjects()
    if ids:
        rs.DeleteObjects(ids)


def choose_dxf_path():
    if DXF_PATH and os.path.isfile(DXF_PATH):
        return DXF_PATH
    return rs.OpenFileName("Choisir le DXF a importer", "DXF Files (*.dxf)|*.dxf||")


def import_dxf(path):
    # Utilise la commande Rhino pour garantir le meme comportement qu'un import manuel.
    command = '-_Import "{}" _Enter'.format(path)
    return rs.Command(command, echo=False)


def set_layer_visibility(target_layer, hide_others):
    visible_layers = target_layer
    if not isinstance(visible_layers, (list, tuple, set)):
        visible_layers = [visible_layers]

    layers = rs.LayerNames() or []
    for layer in layers:
        rs.LayerVisible(layer, True)
        if hide_others and layer not in visible_layers:
            rs.LayerVisible(layer, False)

    if visible_layers and rs.IsLayer(visible_layers[0]):
        rs.CurrentLayer(visible_layers[0])


def zoom_to_layer(layer_name):
    ids = rs.ObjectsByLayer(layer_name, select=False) or []
    if not ids:
        print("Aucun objet trouve sur la couche '{}'.".format(layer_name))
        return

    rs.SelectObjects(ids)
    rs.Command("_Zoom _Selected", echo=False)
    rs.UnselectAllObjects()


def _bbox_area(obj_id):
    bbox = rs.BoundingBox(obj_id)
    if not bbox or len(bbox) < 4:
        return -1.0
    width = abs(bbox[1].X - bbox[0].X)
    height = abs(bbox[3].Y - bbox[0].Y)
    return width * height


def find_largest_outer_edgecut(layer_name, object_ids=None):
    ids = filter_object_ids_by_layer(object_ids, layer_name) if object_ids is not None else (rs.ObjectsByLayer(layer_name, select=False) or [])
    if not ids:
        return None

    candidates = []
    for obj_id in ids:
        if not rs.IsCurve(obj_id):
            continue
        if not rs.IsCurveClosed(obj_id):
            continue
        area = _bbox_area(obj_id)
        if area > 0:
            candidates.append((area, obj_id))

    if not candidates:
        joined = rs.JoinCurves(ids, delete_input=False)
        joined_ids = joined if isinstance(joined, list) else ([joined] if joined else [])
        for obj_id in joined_ids:
            if not rs.IsCurve(obj_id):
                continue
            if not rs.IsCurveClosed(obj_id):
                continue
            area = _bbox_area(obj_id)
            if area > 0:
                candidates.append((area, obj_id))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def style_outer_edgecut(obj_id):
    if not obj_id:
        return
    rs.ObjectColorSource(obj_id, 1)
    rs.ObjectColor(obj_id, (0, 180, 60))
    try:
        rs.ObjectPrintWidthSource(obj_id, 1)
        rs.ObjectPrintWidth(obj_id, 0.45)
    except Exception:
        pass


def hide_other_edgecuts(layer_name, keep_id, object_ids=None):
    ids = filter_object_ids_by_layer(object_ids, layer_name) if object_ids is not None else (rs.ObjectsByLayer(layer_name, select=False) or [])
    for obj_id in ids:
        if keep_id and obj_id == keep_id:
            rs.ShowObject(obj_id)
        else:
            rs.HideObject(obj_id)


def zoom_to_objects(ids):
    ids = [obj_id for obj_id in ids if obj_id and rs.IsObject(obj_id)]
    if not ids:
        return
    rs.SelectObjects(ids)
    rs.Command("_Zoom _Selected", echo=False)
    rs.UnselectAllObjects()


def ensure_layer(layer_name, color=None):
    if not rs.IsLayer(layer_name):
        rs.AddLayer(layer_name, color)
    elif color is not None:
        rs.LayerColor(layer_name, color)


def filter_object_ids_by_layer(object_ids, layer_name):
    out = []
    for obj_id in object_ids or []:
        if not obj_id or not rs.IsObject(obj_id):
            continue
        if rs.ObjectLayer(obj_id) == layer_name:
            out.append(obj_id)
    return out


def curve_bbox_extents(obj_id):
    bbox = rs.BoundingBox(obj_id)
    if not bbox or len(bbox) < 4:
        return None
    xs = [pt.X for pt in bbox]
    ys = [pt.Y for pt in bbox]
    zs = [pt.Z for pt in bbox]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _warn(message):
    print("[WARN] {}".format(message))


def outer_offset_x_bounds(xmin, xmax, offset):
    return xmin - offset, xmax + offset


def hinge_body_x_offset():
    return PCB_OUTER_OFFSET + HINGE_BODY_X_OFFSET_DELTA


def jig_plate_x_bounds(xmin, xmax):
    return outer_offset_x_bounds(xmin, xmax, PCB_OUTER_OFFSET)


def jig_plate_y_max(ymax):
    return ymax + PCB_OUTER_OFFSET


def support_plate_2_x_bounds(xmin, xmax):
    return outer_offset_x_bounds(xmin, xmax, PCB_OUTER_OFFSET)


def support_plate_2_y_max(ymax):
    return ymax + PCB_OUTER_OFFSET


def support_plate_1_x_bounds(xmin, xmax):
    return outer_offset_x_bounds(xmin, xmax, PCB_OUTER_OFFSET + SUPPORT_OUTER_OVERHANG)


def support_plate_1_y_max(ymax):
    return ymax + PCB_OUTER_OFFSET + SUPPORT_OUTER_OVERHANG


def hinge_body_x_bounds(xmin, xmax):
    return outer_offset_x_bounds(xmin, xmax, hinge_body_x_offset())


def validate_global_parameters():
    if HINGE_AXIS_DIAMETER <= JIG_AXIS_DIAMETER:
        _warn(
            "Le diametre d'axe support ({:.3f}) est <= au diametre d'axe jig ({:.3f}).".format(
                HINGE_AXIS_DIAMETER, JIG_AXIS_DIAMETER
            )
        )

    if JIG_PLATE_ZMAX <= JIG_PLATE_ZMIN:
        _warn("Le plateau du jig a une epaisseur nulle ou negative.")

    if PCB_OUTER_OFFSET < 0.0:
        _warn("PCB_OUTER_OFFSET est negatif, le jig et le support vont se retracter vers l'interieur du PCB.")

    if (PCB_OUTER_OFFSET + SUPPORT_OUTER_OVERHANG) <= 0.0:
        _warn("Le plateau support principal n'a plus de debord positif autour du PCB.")

    if hinge_body_x_offset() <= 0.0:
        _warn("Le corps de charniere ne depasse plus le PCB en X.")

    if JIG_BOTTOM_SKIN_THICKNESS <= 0.0:
        _warn("L'epaisseur de peau du jig est <= 0.")
    elif JIG_BOTTOM_SKIN_THICKNESS >= (JIG_PLATE_ZMAX - JIG_PLATE_ZMIN):
        _warn(
            "L'epaisseur de peau du jig ({:.3f}) est >= a l'epaisseur du plateau ({:.3f}).".format(
                JIG_BOTTOM_SKIN_THICKNESS, JIG_PLATE_ZMAX - JIG_PLATE_ZMIN
            )
        )

    if PCB_SEAT_ZMAX <= PCB_SEAT_ZMIN:
        _warn("La decoupe d'empreinte PCB a une epaisseur nulle ou negative.")

    if JIG_HINGE_CLEARANCE_ZMAX <= JIG_HINGE_CLEARANCE_ZMIN:
        _warn("La decoupe de degagement de charniere du jig a une epaisseur nulle ou negative.")

    if MASK_JIG_HEIGHT <= 0.0:
        _warn("La hauteur du jig masque est <= 0.")

    if MASK_JIG_MASK_POCKET_DEPTH <= 0.0 or MASK_JIG_MASK_POCKET_DEPTH >= MASK_JIG_HEIGHT:
        _warn("La poche du masque doit etre comprise entre 0 et la hauteur du jig masque.")

    if MASK_JIG_PCB_CUT_DEPTH_FROM_TOP <= 0.0 or MASK_JIG_PCB_CUT_DEPTH_FROM_TOP >= MASK_JIG_HEIGHT:
        _warn("La decoupe PCB du jig masque doit etre comprise entre 0 et la hauteur du jig masque.")


def validate_geometry_parameters(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    width_x = xmax - xmin
    height_y = ymax - ymin
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    y_contact_hinge_body = axis_y + HINGE_BODY_WIDTH_Y / 2.0
    jig_x0, jig_x1 = jig_plate_x_bounds(xmin, xmax)
    support_x0, support_x1 = support_plate_1_x_bounds(xmin, xmax)
    body_x0, body_x1 = hinge_body_x_bounds(xmin, xmax)

    if jig_x1 <= jig_x0:
        _warn("Le plateau du jig n'a plus de largeur en X avec les insets actuels.")

    if y_contact_hinge_body >= jig_plate_y_max(ymax):
        _warn("Le plateau du jig n'a plus de hauteur utile en Y.")

    if body_x0 <= support_x0 or body_x1 >= support_x1:
        _warn("Le corps de charniere atteint ou depasse les bords du support, les montants peuvent devenir nuls.")

    if (width_x - LEVER_CUT_SIDE_MARGIN_TOTAL) < LEVER_CUT_MIN_WIDTH:
        _warn(
            "La decoupe de levier est contrainte par le minimum de {:.3f} mm sur ce PCB.".format(
                LEVER_CUT_MIN_WIDTH
            )
        )

    if (width_x <= 2.0 * EJECTION_MARGIN_X) or (height_y <= 2.0 * EJECTION_MARGIN_Y):
        _warn("L'ouverture d'ejection rectangulaire ne rentre pas, le fallback cylindre sera utilise.")

    if PCB_SEAT_ZMIN < 0.0 or PCB_SEAT_ZMAX > JIG_POST_ZMAX:
        _warn("La decoupe d'empreinte PCB sort de la plage Z habituelle du support/jig.")

    if JIG_PLATE_ZMIN < PCB_SEAT_ZMAX:
        _warn(
            "Le dessus de l'empreinte PCB ({:.3f}) depasse sous le debut du plateau jig ({:.3f}).".format(
                PCB_SEAT_ZMAX, JIG_PLATE_ZMIN
            )
        )


def create_hinge_axis_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    x0 = xmin - HINGE_AXIS_EXTRA_X_MIN
    x1 = xmax + HINGE_AXIS_EXTRA_X_MAX
    radius = HINGE_AXIS_DIAMETER / 2.0
    height = x1 - x0

    ensure_layer(HINGE_AXIS_LAYER, HINGE_AXIS_COLOR)
    base_plane = rs.MovePlane(rs.WorldYZPlane(), (x0, axis_y, HINGE_AXIS_Z))
    cylinder_id = rs.AddCylinder(base_plane, height, radius, cap=True)
    if cylinder_id:
        rs.ObjectLayer(cylinder_id, HINGE_AXIS_LAYER)
        rs.ObjectColorSource(cylinder_id, 1)
        rs.ObjectColor(cylinder_id, HINGE_AXIS_COLOR)
    return cylinder_id


def create_jig_axis_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    x0 = xmin - HINGE_AXIS_EXTRA_X_MIN
    x1 = xmax + HINGE_AXIS_EXTRA_X_MAX
    radius = JIG_AXIS_DIAMETER / 2.0
    height = x1 - x0

    ensure_layer(JIG_AXIS_LAYER, JIG_AXIS_COLOR)
    base_plane = rs.MovePlane(rs.WorldYZPlane(), (x0, axis_y, HINGE_AXIS_Z))
    cylinder_id = rs.AddCylinder(base_plane, height, radius, cap=True)
    if cylinder_id:
        rs.ObjectLayer(cylinder_id, JIG_AXIS_LAYER)
        rs.ObjectColorSource(cylinder_id, 1)
        rs.ObjectColor(cylinder_id, JIG_AXIS_COLOR)
    return cylinder_id


def create_hinge_profile_yz(x_plane, axis_y, width_y, zmin, zmax, top_fillet_radius, bottom_left_fillet_radius):
    y0 = axis_y - width_y / 2.0
    y1 = axis_y + width_y / 2.0
    height_z = zmax - zmin
    rt = min(top_fillet_radius, width_y / 2.0, height_z)
    rb = min(bottom_left_fillet_radius, width_y / 2.0, height_z)

    if rb > 1e-9:
        p0 = (x_plane, y0 + rb, zmin)
        p6 = (x_plane, y0, zmin + rb)
    else:
        p0 = (x_plane, y0, zmin)
        p6 = p0

    p1 = (x_plane, y1, zmin)
    p2 = (x_plane, y1, zmax - rt)
    p3 = (x_plane, y1 - rt, zmax)
    p4 = (x_plane, y0 + rt, zmax)
    p5 = (x_plane, y0, zmax - rt)

    segments = []
    segments.append(rs.AddLine(p0, p1))
    segments.append(rs.AddLine(p1, p2))

    plane_tr = rs.PlaneFromFrame((x_plane, y1 - rt, zmax - rt), (0, 1, 0), (0, 0, 1))
    segments.append(rs.AddArc(plane_tr, rt, 90.0))

    segments.append(rs.AddLine(p3, p4))

    plane_tl = rs.PlaneFromFrame((x_plane, y0 + rt, zmax - rt), (0, 0, 1), (0, -1, 0))
    segments.append(rs.AddArc(plane_tl, rt, 90.0))

    if rb > 1e-9:
        segments.append(rs.AddLine(p5, p6))
        plane_bl = rs.PlaneFromFrame((x_plane, y0 + rb, zmin + rb), (0, -1, 0), (0, 0, -1))
        segments.append(rs.AddArc(plane_bl, rb, 90.0))
    else:
        segments.append(rs.AddLine(p5, p0))

    segments = [seg for seg in segments if seg]
    expected_count = 7 if rb > 1e-9 else 6
    if len(segments) != expected_count:
        if segments:
            rs.DeleteObjects(segments)
        return None

    joined = rs.JoinCurves(segments, delete_input=True)
    if not joined:
        return None
    if isinstance(joined, list):
        return joined[0]
    return joined


def create_hinge_body_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    x0, x1 = hinge_body_x_bounds(xmin, xmax)
    z0 = HINGE_BODY_ZMIN

    ensure_layer(HINGE_BODY_LAYER, HINGE_BODY_COLOR)
    profile_id = create_hinge_profile_yz(
        x0,
        axis_y,
        HINGE_BODY_WIDTH_Y,
        HINGE_BODY_ZMIN,
        HINGE_BODY_ZMIN + HINGE_BODY_HEIGHT_Z,
        HINGE_BODY_FILLET_RADIUS,
        0.0,
    )
    if not profile_id:
        return None

    body_id = rs.ExtrudeCurveStraight(profile_id, (x0, axis_y, z0), (x1, axis_y, z0))
    rs.DeleteObject(profile_id)
    if not body_id:
        return None

    rs.CapPlanarHoles(body_id)

    rs.ObjectLayer(body_id, HINGE_BODY_LAYER)
    rs.ObjectColorSource(body_id, 1)
    rs.ObjectColor(body_id, HINGE_BODY_COLOR)
    return body_id


def create_jig_hinge_posts_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return []

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    body_xmin, body_xmax = hinge_body_x_bounds(xmin, xmax)
    support_xmin, support_xmax = support_plate_1_x_bounds(xmin, xmax)

    ensure_layer(JIG_POSTS_LAYER, JIG_POSTS_COLOR)
    profile_left = create_hinge_profile_yz(
        body_xmin,
        axis_y,
        HINGE_BODY_WIDTH_Y,
        JIG_POST_ZMIN,
        JIG_POST_ZMAX,
        HINGE_BODY_FILLET_RADIUS,
        JIG_POST_BOTTOM_FILLET_RADIUS,
    )
    profile_right = create_hinge_profile_yz(
        body_xmax,
        axis_y,
        HINGE_BODY_WIDTH_Y,
        JIG_POST_ZMIN,
        JIG_POST_ZMAX,
        HINGE_BODY_FILLET_RADIUS,
        JIG_POST_BOTTOM_FILLET_RADIUS,
    )
    if not profile_left or not profile_right:
        if profile_left:
            rs.DeleteObject(profile_left)
        if profile_right:
            rs.DeleteObject(profile_right)
        return []

    post_ids = []
    left_post = rs.ExtrudeCurveStraight(profile_left, (body_xmin, axis_y, 0.0), (support_xmin, axis_y, 0.0))
    right_post = rs.ExtrudeCurveStraight(profile_right, (body_xmax, axis_y, 0.0), (support_xmax, axis_y, 0.0))
    rs.DeleteObject(profile_left)
    rs.DeleteObject(profile_right)

    if left_post:
        rs.CapPlanarHoles(left_post)
        rs.ObjectLayer(left_post, JIG_POSTS_LAYER)
        rs.ObjectColorSource(left_post, 1)
        rs.ObjectColor(left_post, JIG_POSTS_COLOR)
        post_ids.append(left_post)

    if right_post:
        rs.CapPlanarHoles(right_post)
        rs.ObjectLayer(right_post, JIG_POSTS_LAYER)
        rs.ObjectColorSource(right_post, 1)
        rs.ObjectColor(right_post, JIG_POSTS_COLOR)
        post_ids.append(right_post)

    return post_ids


def create_jig_plate_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    y_contact_posts = axis_y + HINGE_BODY_WIDTH_Y / 2.0

    x0, x1 = jig_plate_x_bounds(xmin, xmax)
    y0 = y_contact_posts
    y1 = jig_plate_y_max(ymax)
    z0 = JIG_PLATE_ZMIN
    z1 = JIG_PLATE_ZMAX

    if x1 <= x0 or y1 <= y0 or z1 <= z0:
        return None

    ensure_layer(JIG_PLATE_LAYER, JIG_PLATE_COLOR)
    profile_id = create_top_rounded_profile_xy(x0, x1, y0, y1, JIG_PLATE_TOP_FILLET_RADIUS)
    return extrude_profile_in_z(profile_id, z0, z1, JIG_PLATE_LAYER, JIG_PLATE_COLOR)


def create_top_rounded_profile_xy(x0, x1, y0, y1, radius):
    r = min(radius, abs(x1 - x0) / 2.0, abs(y1 - y0))
    p0 = (x0, y0, 0.0)
    p1 = (x1, y0, 0.0)
    p2 = (x1, y1 - r, 0.0)
    p3 = (x1 - r, y1, 0.0)
    p4 = (x0 + r, y1, 0.0)
    p5 = (x0, y1 - r, 0.0)

    segments = []
    segments.append(rs.AddLine(p0, p1))
    segments.append(rs.AddLine(p1, p2))

    plane_tr = rs.PlaneFromFrame((x1 - r, y1 - r, 0.0), (1, 0, 0), (0, 1, 0))
    segments.append(rs.AddArc(plane_tr, r, 90.0))

    segments.append(rs.AddLine(p3, p4))

    plane_tl = rs.PlaneFromFrame((x0 + r, y1 - r, 0.0), (0, 1, 0), (-1, 0, 0))
    segments.append(rs.AddArc(plane_tl, r, 90.0))

    segments.append(rs.AddLine(p5, p0))
    segments = [seg for seg in segments if seg]
    if len(segments) != 6:
        if segments:
            rs.DeleteObjects(segments)
        return None

    joined = rs.JoinCurves(segments, delete_input=True)
    if not joined:
        return None
    if isinstance(joined, list):
        return joined[0]
    return joined


def create_rounded_rectangle_profile_xy(x0, x1, y0, y1, radius):
    r = min(radius, abs(x1 - x0) / 2.0, abs(y1 - y0) / 2.0)
    if r <= 1e-9:
        return rs.AddPolyline(
            [
                (x0, y0, 0.0),
                (x1, y0, 0.0),
                (x1, y1, 0.0),
                (x0, y1, 0.0),
                (x0, y0, 0.0),
            ]
        )
    points = [
        (x0 + r, y0, 0.0),
        (x1 - r, y0, 0.0),
        (x1, y0 + r, 0.0),
        (x1, y1 - r, 0.0),
        (x1 - r, y1, 0.0),
        (x0 + r, y1, 0.0),
        (x0, y1 - r, 0.0),
        (x0, y0 + r, 0.0),
    ]

    segments = []
    segments.append(rs.AddLine(points[0], points[1]))
    plane_br = rs.PlaneFromFrame((x1 - r, y0 + r, 0.0), (0, -1, 0), (1, 0, 0))
    segments.append(rs.AddArc(plane_br, r, 90.0))
    segments.append(rs.AddLine(points[2], points[3]))
    plane_tr = rs.PlaneFromFrame((x1 - r, y1 - r, 0.0), (1, 0, 0), (0, 1, 0))
    segments.append(rs.AddArc(plane_tr, r, 90.0))
    segments.append(rs.AddLine(points[4], points[5]))
    plane_tl = rs.PlaneFromFrame((x0 + r, y1 - r, 0.0), (0, 1, 0), (-1, 0, 0))
    segments.append(rs.AddArc(plane_tl, r, 90.0))
    segments.append(rs.AddLine(points[6], points[7]))
    plane_bl = rs.PlaneFromFrame((x0 + r, y0 + r, 0.0), (-1, 0, 0), (0, -1, 0))
    segments.append(rs.AddArc(plane_bl, r, 90.0))

    segments = [seg for seg in segments if seg]
    if len(segments) != 8:
        if segments:
            rs.DeleteObjects(segments)
        return None

    joined = rs.JoinCurves(segments, delete_input=True)
    if not joined:
        return None
    if isinstance(joined, list):
        return joined[0]
    return joined


def extrude_profile_in_z(profile_id, zmin, zmax, layer_name, color):
    if not profile_id:
        return None
    height = zmax - zmin
    solid_id = rs.ExtrudeCurveStraight(profile_id, (0.0, 0.0, 0.0), (0.0, 0.0, height))
    rs.DeleteObject(profile_id)
    if not solid_id:
        return None
    rs.CapPlanarHoles(solid_id)
    if abs(zmin) > 1e-9:
        rs.MoveObject(solid_id, (0.0, 0.0, zmin))
    rs.ObjectLayer(solid_id, layer_name)
    rs.ObjectColorSource(solid_id, 1)
    rs.ObjectColor(solid_id, color)
    return solid_id


def extrude_curve_in_z(curve_id, zmin, zmax, layer_name, color):
    if not curve_id:
        return None
    height = zmax - zmin
    if height <= 0.0:
        return None
    copy_id = rs.CopyObject(curve_id)
    if not copy_id:
        return None
    solid_id = rs.ExtrudeCurveStraight(copy_id, (0.0, 0.0, 0.0), (0.0, 0.0, height))
    rs.DeleteObject(copy_id)
    if not solid_id:
        return None
    rs.CapPlanarHoles(solid_id)
    if abs(zmin) > 1e-9:
        rs.MoveObject(solid_id, (0.0, 0.0, zmin))
    rs.ObjectLayer(solid_id, layer_name)
    rs.ObjectColorSource(solid_id, 1)
    rs.ObjectColor(solid_id, color)
    return solid_id


def create_plate_solids_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return []

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    contact_hinge_body_y = axis_y + HINGE_BODY_WIDTH_Y / 2.0

    ensure_layer(PLATE_1_LAYER, PLATE_1_COLOR)
    ensure_layer(PLATE_2_LAYER, PLATE_2_COLOR)
    ensure_layer(PLATE_3_LAYER, PLATE_3_COLOR)

    solids = {"plate_1": None, "plate_2": None, "plate_3": None}

    plate_1_x0, plate_1_x1 = support_plate_1_x_bounds(xmin, xmax)
    profile1 = create_top_rounded_profile_xy(
        plate_1_x0,
        plate_1_x1,
        axis_y + PLATE_1_OFFSET_FROM_AXIS_Y,
        support_plate_1_y_max(ymax),
        PLATE_1_TOP_FILLET_RADIUS,
    )
    solid1 = extrude_profile_in_z(profile1, PLATE_1_ZMIN, PLATE_1_ZMAX, PLATE_1_LAYER, PLATE_1_COLOR)
    if solid1:
        solids["plate_1"] = solid1

    plate_2_x0, plate_2_x1 = support_plate_2_x_bounds(xmin, xmax)
    plate_2_y1 = support_plate_2_y_max(ymax)
    profile2a = create_top_rounded_profile_xy(
        plate_2_x0,
        plate_2_x1,
        contact_hinge_body_y,
        plate_2_y1,
        PLATE_2_TOP_FILLET_RADIUS,
    )
    solid2a = extrude_profile_in_z(profile2a, PLATE_2A_ZMIN, PLATE_2A_ZMAX, PLATE_2_LAYER, PLATE_2_COLOR)
    if solid2a:
        solids["plate_2"] = solid2a

    profile2b = create_top_rounded_profile_xy(
        plate_2_x0,
        plate_2_x1,
        contact_hinge_body_y,
        plate_2_y1,
        PLATE_2_TOP_FILLET_RADIUS,
    )
    solid2b = extrude_profile_in_z(profile2b, PLATE_2B_ZMIN, PLATE_2B_ZMAX, PLATE_3_LAYER, PLATE_3_COLOR)
    if solid2b:
        solids["plate_3"] = solid2b

    return solids


def boolean_union_keep(inputs, layer_name, color):
    solid_ids = [obj_id for obj_id in inputs if obj_id]
    if not solid_ids:
        return None
    if len(solid_ids) == 1:
        return solid_ids[0]

    result = rs.BooleanUnion(solid_ids, delete_input=False)
    if not result:
        print("Echec de l'union booleenne.")
        return solid_ids[0]

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, layer_name)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, color)
    for obj_id in solid_ids:
        if rs.IsObject(obj_id):
            rs.HideObject(obj_id)
    return result_id


def boolean_difference_keep(base_id, cutter_id, layer_name, color):
    if not base_id or not cutter_id:
        return base_id

    result = rs.BooleanDifference(base_id, cutter_id, delete_input=False)
    if not result:
        print("Echec de la difference booleenne.")
        return base_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, layer_name)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, color)
    if rs.IsObject(base_id):
        rs.HideObject(base_id)
    if rs.IsObject(cutter_id):
        rs.HideObject(cutter_id)
    return result_id


def boolean_difference_delete(base_id, cutter_id, layer_name, color, error_message):
    if not base_id or not cutter_id:
        return base_id

    result = rs.BooleanDifference(base_id, cutter_id, delete_input=False)
    if not result:
        print(error_message)
        return base_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, layer_name)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, color)
    delete_objects([base_id, cutter_id])
    return result_id


def hide_objects(ids):
    for obj_id in ids:
        if obj_id and rs.IsObject(obj_id):
            rs.HideObject(obj_id)


def delete_objects(ids):
    ids = [obj_id for obj_id in ids if obj_id and rs.IsObject(obj_id)]
    if ids:
        rs.DeleteObjects(ids)


def cleanup_construction_geometry(keep_ids, keep_layers):
    keep_ids = set([obj_id for obj_id in keep_ids if obj_id and rs.IsObject(obj_id)])
    keep_layers = set(keep_layers)
    all_ids = rs.AllObjects() or []
    delete_ids = []

    for obj_id in all_ids:
        if obj_id in keep_ids:
            continue
        layer_name = rs.ObjectLayer(obj_id)
        if layer_name in keep_layers:
            continue
        delete_ids.append(obj_id)

    delete_objects(delete_ids)


def delete_empty_layers(keep_layers):
    keep_layers = set(keep_layers)
    if not rs.IsLayer("Default"):
        rs.AddLayer("Default")
    rs.CurrentLayer("Default")
    layers = rs.LayerNames() or []
    for layer_name in reversed(layers):
        if layer_name in keep_layers:
            continue
        if layer_name == "Default":
            continue
        if not rs.IsLayer(layer_name):
            continue
        layer_objects = rs.ObjectsByLayer(layer_name, select=False) or []
        if layer_objects:
            continue
        try:
            rs.DeleteLayer(layer_name)
        except Exception:
            pass

    # Rhino garde parfois des calques vides apres suppression d'objets :
    # on lance une purge explicite pour ne conserver que les calques utiles.
    try:
        rs.Command("-_Purge _Pause _Layers=_Yes _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Linetypes=_No _Textures=_No _Environments=_No _Bitmaps=_No _Enter", echo=False)
    except Exception:
        pass


def create_ejection_cut_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    inner_xmin = xmin + EJECTION_MARGIN_X
    inner_xmax = xmax - EJECTION_MARGIN_X
    inner_ymin = ymin + EJECTION_MARGIN_Y
    inner_ymax = ymax - EJECTION_MARGIN_Y
    height = EJECTION_ZMAX - EJECTION_ZMIN

    ensure_layer(EJECTION_CUT_LAYER, EJECTION_CUT_COLOR)

    if inner_xmax > inner_xmin and inner_ymax > inner_ymin:
        corner1 = (inner_xmin, inner_ymin, EJECTION_ZMIN)
        corner2 = (inner_xmax, inner_ymax, EJECTION_ZMAX)
        cut_id = rs.AddBox(
            [
                (corner1[0], corner1[1], corner1[2]),
                (corner2[0], corner1[1], corner1[2]),
                (corner2[0], corner2[1], corner1[2]),
                (corner1[0], corner2[1], corner1[2]),
                (corner1[0], corner1[1], corner2[2]),
                (corner2[0], corner1[1], corner2[2]),
                (corner2[0], corner2[1], corner2[2]),
                (corner1[0], corner2[1], corner2[2]),
            ]
        )
    else:
        dim_x = xmax - xmin
        dim_y = ymax - ymin
        diameter = min(dim_x, dim_y)
        radius = diameter / 2.0
        center = ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, EJECTION_ZMIN)
        base_plane = rs.MovePlane(rs.WorldXYPlane(), center)
        cut_id = rs.AddCylinder(base_plane, height, radius, cap=True)

    if cut_id:
        rs.ObjectLayer(cut_id, EJECTION_CUT_LAYER)
        rs.ObjectColorSource(cut_id, 1)
        rs.ObjectColor(cut_id, EJECTION_CUT_COLOR)
    return cut_id


def subtract_ejection_cut_from_support(support_id, cut_id):
    if not support_id or not cut_id:
        return support_id

    result = rs.BooleanDifference(support_id, cut_id, delete_input=False)
    if not result:
        print("Echec de la soustraction de l'ouverture d'ejection.")
        return support_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, SUPPORT_RESULT_LAYER)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, SUPPORT_RESULT_COLOR)
    if rs.IsObject(support_id):
        rs.HideObject(support_id)
    if rs.IsObject(cut_id):
        rs.HideObject(cut_id)
    return result_id


def create_lever_cut_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    width_x = max(LEVER_CUT_MIN_WIDTH, (xmax - xmin) - LEVER_CUT_SIDE_MARGIN_TOTAL)
    cx = (xmin + xmax) / 2.0
    x0 = cx - width_x / 2.0
    x1 = cx + width_x / 2.0
    y0 = ymax
    y1 = ymax + LEVER_CUT_YMAX_EXTRA
    z0 = LEVER_CUT_ZMIN
    z1 = LEVER_CUT_ZMAX

    ensure_layer(LEVER_CUT_LAYER, LEVER_CUT_COLOR)
    cut_id = rs.AddBox(
        [
            (x0, y0, z0),
            (x1, y0, z0),
            (x1, y1, z0),
            (x0, y1, z0),
            (x0, y0, z1),
            (x1, y0, z1),
            (x1, y1, z1),
            (x0, y1, z1),
        ]
    )
    if cut_id:
        rs.ObjectLayer(cut_id, LEVER_CUT_LAYER)
        rs.ObjectColorSource(cut_id, 1)
        rs.ObjectColor(cut_id, LEVER_CUT_COLOR)
    return cut_id


def create_jig_lever_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    width_x = max(LEVER_CUT_MIN_WIDTH, (xmax - xmin) - LEVER_CUT_SIDE_MARGIN_TOTAL)
    cx = (xmin + xmax) / 2.0
    x0 = cx - width_x / 2.0
    x1 = cx + width_x / 2.0
    y0 = jig_plate_y_max(ymax)
    y1 = support_plate_1_y_max(ymax) + JIG_LEVER_OVERHANG_Y
    z0 = JIG_LEVER_ZMIN
    z1 = JIG_LEVER_ZMAX

    ensure_layer(JIG_LEVER_LAYER, JIG_LEVER_COLOR)
    lever_id = rs.AddBox(
        [
            (x0, y0, z0),
            (x1, y0, z0),
            (x1, y1, z0),
            (x0, y1, z0),
            (x0, y0, z1),
            (x1, y0, z1),
            (x1, y1, z1),
            (x0, y1, z1),
        ]
    )
    if lever_id:
        rs.ObjectLayer(lever_id, JIG_LEVER_LAYER)
        rs.ObjectColorSource(lever_id, 1)
        rs.ObjectColor(lever_id, JIG_LEVER_COLOR)
    return lever_id


def create_jig_hinge_clearance_cut_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    axis_y = ymin + HINGE_AXIS_OFFSET_FROM_YMIN
    y_contact_hinge_body = axis_y + HINGE_BODY_WIDTH_Y / 2.0
    x0, x1 = hinge_body_x_bounds(xmin, xmax)
    y0 = y_contact_hinge_body
    y1 = y_contact_hinge_body + JIG_HINGE_CLEARANCE_DEPTH_Y
    z0 = JIG_HINGE_CLEARANCE_ZMIN
    z1 = JIG_HINGE_CLEARANCE_ZMAX

    ensure_layer(JIG_HINGE_CLEARANCE_CUT_LAYER, JIG_HINGE_CLEARANCE_CUT_COLOR)
    cut_id = rs.AddBox(
        [
            (x0, y0, z0),
            (x1, y0, z0),
            (x1, y1, z0),
            (x0, y1, z0),
            (x0, y0, z1),
            (x1, y0, z1),
            (x1, y1, z1),
            (x0, y1, z1),
        ]
    )
    if cut_id:
        rs.ObjectLayer(cut_id, JIG_HINGE_CLEARANCE_CUT_LAYER)
        rs.ObjectColorSource(cut_id, 1)
        rs.ObjectColor(cut_id, JIG_HINGE_CLEARANCE_CUT_COLOR)
    return cut_id


def subtract_hinge_clearance_from_jig_plate(jig_plate_id, cut_id):
    if not jig_plate_id or not cut_id:
        return jig_plate_id

    result = rs.BooleanDifference(jig_plate_id, cut_id, delete_input=False)
    if not result:
        print("Echec de la soustraction du degagement de charniere dans le plateau du jig.")
        return jig_plate_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, JIG_PLATE_LAYER)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, JIG_PLATE_COLOR)
    if rs.IsObject(jig_plate_id):
        rs.HideObject(jig_plate_id)
    if rs.IsObject(cut_id):
        rs.HideObject(cut_id)
    return result_id


def create_jig_plate_pocket_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    z0 = JIG_PLATE_ZMIN + JIG_BOTTOM_SKIN_THICKNESS
    z1 = JIG_PLATE_ZMAX
    if z1 <= z0:
        return None

    ensure_layer(JIG_POCKET_CUT_LAYER, JIG_POCKET_CUT_COLOR)
    cut_id = rs.AddBox(
        [
            (xmin, ymin, z0),
            (xmax, ymin, z0),
            (xmax, ymax, z0),
            (xmin, ymax, z0),
            (xmin, ymin, z1),
            (xmax, ymin, z1),
            (xmax, ymax, z1),
            (xmin, ymax, z1),
        ]
    )
    if cut_id:
        rs.ObjectLayer(cut_id, JIG_POCKET_CUT_LAYER)
        rs.ObjectColorSource(cut_id, 1)
        rs.ObjectColor(cut_id, JIG_POCKET_CUT_COLOR)
    return cut_id


def create_openings_cutters_for_jig(curve_ids=None):
    curve_ids = curve_ids if curve_ids is not None else (rs.ObjectsByLayer(OPENINGS_LAYER, select=False) or [])
    cutters = []
    ensure_layer(JIG_OPENINGS_CUT_LAYER, JIG_OPENINGS_CUT_COLOR)

    for curve_id in curve_ids:
        if not rs.IsCurve(curve_id) or not rs.IsCurveClosed(curve_id):
            continue
        cutter_id = rs.ExtrudeCurveStraight(
            curve_id,
            (0.0, 0.0, 0.0),
            (0.0, 0.0, JIG_PLATE_ZMAX),
        )
        if not cutter_id:
            continue
        rs.CapPlanarHoles(cutter_id)
        rs.ObjectLayer(cutter_id, JIG_OPENINGS_CUT_LAYER)
        rs.ObjectColorSource(cutter_id, 1)
        rs.ObjectColor(cutter_id, JIG_OPENINGS_CUT_COLOR)
        cutters.append(cutter_id)
    return cutters


def subtract_multiple_cutters_from_jig_plate(jig_plate_id, cutter_ids):
    result_id = jig_plate_id
    for cutter_id in cutter_ids:
        if not result_id or not cutter_id:
            continue
        result = rs.BooleanDifference(result_id, cutter_id, delete_input=False)
        if not result:
            print("Echec de soustraction d'un cutter du plateau du jig.")
            continue

        if isinstance(result, list):
            new_result_id = result[0]
        else:
            new_result_id = result

        rs.ObjectLayer(new_result_id, JIG_PLATE_LAYER)
        rs.ObjectColorSource(new_result_id, 1)
        rs.ObjectColor(new_result_id, JIG_PLATE_COLOR)
        if rs.IsObject(result_id):
            rs.HideObject(result_id)
        if rs.IsObject(cutter_id):
            rs.HideObject(cutter_id)
        result_id = new_result_id
    return result_id


def union_jig_parts(part_ids):
    solid_ids = [obj_id for obj_id in part_ids if obj_id]
    if not solid_ids:
        return None
    ensure_layer(JIG_RESULT_LAYER, JIG_RESULT_COLOR)
    result_id = boolean_union_keep(solid_ids, JIG_RESULT_LAYER, JIG_RESULT_COLOR)
    return result_id


def subtract_jig_axis_from_result(jig_result_id, jig_axis_id):
    if not jig_result_id or not jig_axis_id:
        return jig_result_id

    result = rs.BooleanDifference(jig_result_id, jig_axis_id, delete_input=False)
    if not result:
        print("Echec de la soustraction de l'axe du jig.")
        return jig_result_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, JIG_RESULT_LAYER)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, JIG_RESULT_COLOR)
    if rs.IsObject(jig_result_id):
        rs.HideObject(jig_result_id)
    if rs.IsObject(jig_axis_id):
        rs.HideObject(jig_axis_id)
    return result_id


def subtract_lever_cut_from_support(support_id, cut_id):
    if not support_id or not cut_id:
        return support_id

    result = rs.BooleanDifference(support_id, cut_id, delete_input=False)
    if not result:
        print("Echec de la soustraction de la decoupe de levier.")
        return support_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, SUPPORT_RESULT_LAYER)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, SUPPORT_RESULT_COLOR)
    if rs.IsObject(support_id):
        rs.HideObject(support_id)
    if rs.IsObject(cut_id):
        rs.HideObject(cut_id)
    return result_id


def create_pcb_seat_cut_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    x0 = xmin - PCB_SEAT_MARGIN_XY
    x1 = xmax + PCB_SEAT_MARGIN_XY
    y0 = ymin - PCB_SEAT_MARGIN_XY
    y1 = ymax + PCB_SEAT_MARGIN_XY
    z0 = PCB_SEAT_ZMIN
    z1 = PCB_SEAT_ZMAX

    ensure_layer(PCB_SEAT_CUT_LAYER, PCB_SEAT_CUT_COLOR)
    cut_id = rs.AddBox(
        [
            (x0, y0, z0),
            (x1, y0, z0),
            (x1, y1, z0),
            (x0, y1, z0),
            (x0, y0, z1),
            (x1, y0, z1),
            (x1, y1, z1),
            (x0, y1, z1),
        ]
    )
    if cut_id:
        rs.ObjectLayer(cut_id, PCB_SEAT_CUT_LAYER)
        rs.ObjectColorSource(cut_id, 1)
        rs.ObjectColor(cut_id, PCB_SEAT_CUT_COLOR)
    return cut_id


def subtract_pcb_seat_cut_from_support(support_id, cut_id):
    if not support_id or not cut_id:
        return support_id

    result = rs.BooleanDifference(support_id, cut_id, delete_input=False)
    if not result:
        print("Echec de la soustraction de l'empreinte PCB dans le support.")
        return support_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, SUPPORT_RESULT_LAYER)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, SUPPORT_RESULT_COLOR)
    if rs.IsObject(support_id):
        rs.HideObject(support_id)
    if rs.IsObject(cut_id):
        rs.HideObject(cut_id)
    return result_id


def subtract_hinge_axis_from_body(body_id, axis_id):
    if not body_id or not axis_id:
        return body_id

    result = rs.BooleanDifference(body_id, axis_id, delete_input=False)
    if not result:
        print("Echec de la difference booleenne corps - axe.")
        return body_id

    if isinstance(result, list):
        result_id = result[0]
    else:
        result_id = result

    rs.ObjectLayer(result_id, HINGE_BODY_LAYER)
    rs.ObjectColorSource(result_id, 1)
    rs.ObjectColor(result_id, HINGE_BODY_COLOR)
    rs.HideObject(body_id)
    rs.HideObject(axis_id)
    return result_id


def create_mask_jig_base_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    outer_offset = SOLDER_MASK_BORDER + MASK_JIG_OUTER_MARGIN
    x0 = xmin - outer_offset
    x1 = xmax + outer_offset
    y0 = ymin - outer_offset
    y1 = ymax + outer_offset

    ensure_layer(MASK_JIG_RESULT_LAYER, MASK_JIG_RESULT_COLOR)
    profile_id = create_rounded_rectangle_profile_xy(
        x0, x1, y0, y1, MASK_JIG_OUTER_FILLET_RADIUS
    )
    return extrude_profile_in_z(
        profile_id,
        0.0,
        MASK_JIG_HEIGHT,
        MASK_JIG_RESULT_LAYER,
        MASK_JIG_RESULT_COLOR,
    )


def create_mask_jig_mask_pocket_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return None

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    x0 = xmin - SOLDER_MASK_BORDER - MASK_JIG_MASK_CLEARANCE_XY
    x1 = xmax + SOLDER_MASK_BORDER + MASK_JIG_MASK_CLEARANCE_XY
    y0 = ymin - SOLDER_MASK_BORDER - MASK_JIG_MASK_CLEARANCE_XY
    y1 = ymax + SOLDER_MASK_BORDER + MASK_JIG_MASK_CLEARANCE_XY
    z0 = MASK_JIG_HEIGHT - MASK_JIG_MASK_POCKET_DEPTH
    z1 = MASK_JIG_HEIGHT

    profile_id = create_rounded_rectangle_profile_xy(x0, x1, y0, y1, 0.0)
    return extrude_profile_in_z(
        profile_id,
        z0,
        z1,
        MASK_JIG_RESULT_LAYER,
        MASK_JIG_RESULT_COLOR,
    )


def create_mask_jig_pcb_cut_from_outer_frame(outer_edgecut_id):
    z0 = MASK_JIG_HEIGHT - MASK_JIG_PCB_CUT_DEPTH_FROM_TOP
    z1 = MASK_JIG_HEIGHT
    return extrude_curve_in_z(
        outer_edgecut_id,
        z0,
        z1,
        MASK_JIG_RESULT_LAYER,
        MASK_JIG_RESULT_COLOR,
    )


def create_mask_jig_ejection_cuts_from_outer_frame(outer_edgecut_id):
    extents = curve_bbox_extents(outer_edgecut_id)
    if not extents:
        return []

    xmin, xmax, ymin, ymax, _zmin, _zmax = extents
    dim_x = xmax - xmin
    dim_y = ymax - ymin
    center_x = (xmin + xmax) / 2.0
    center_y = (ymin + ymax) / 2.0
    cuts = []

    if dim_x < MASK_JIG_SMALL_PCB_THRESHOLD or dim_y < MASK_JIG_SMALL_PCB_THRESHOLD:
        radius = min(dim_x, dim_y) / 2.0
        plane = rs.MovePlane(rs.WorldXYPlane(), (center_x, center_y, 0.0))
        cut_id = rs.AddCylinder(plane, MASK_JIG_HEIGHT, radius, cap=True)
        if cut_id:
            cuts.append(cut_id)
        return cuts

    hole_d = MASK_JIG_EJECTION_HOLE_DIAMETER
    pitch = hole_d + MASK_JIG_EJECTION_HOLE_MIN_SPACING
    count_x = max(1, int(math.floor((dim_x - hole_d) / pitch)) + 1)
    count_y = max(1, int(math.floor((dim_y - hole_d) / pitch)) + 1)
    span_x = hole_d + (count_x - 1) * pitch
    span_y = hole_d + (count_y - 1) * pitch
    start_x = center_x - span_x / 2.0 + hole_d / 2.0
    start_y = center_y - span_y / 2.0 + hole_d / 2.0
    radius = hole_d / 2.0

    for ix in range(count_x):
        for iy in range(count_y):
            cx = start_x + ix * pitch
            cy = start_y + iy * pitch
            plane = rs.MovePlane(rs.WorldXYPlane(), (cx, cy, 0.0))
            cut_id = rs.AddCylinder(plane, MASK_JIG_HEIGHT, radius, cap=True)
            if cut_id:
                cuts.append(cut_id)
    return cuts


def subtract_cutters_from_mask_jig(mask_jig_id, cutter_ids):
    result_id = mask_jig_id
    for cutter_id in cutter_ids:
        if not result_id or not cutter_id:
            continue
        result_id = boolean_difference_delete(
            result_id,
            cutter_id,
            MASK_JIG_RESULT_LAYER,
            MASK_JIG_RESULT_COLOR,
            "Echec d'une soustraction sur le jig masque.",
        )
    return result_id


def move_mask_jig_left_of_support(mask_jig_id, support_id):
    if not mask_jig_id:
        return mask_jig_id

    mask_extents = curve_bbox_extents(mask_jig_id)
    if not mask_extents:
        return mask_jig_id

    mask_xmin, mask_xmax, _ymin, _ymax, _zmin, _zmax = mask_extents
    target_right_x = None

    if support_id and rs.IsObject(support_id):
        support_extents = curve_bbox_extents(support_id)
        if support_extents:
            support_xmin, _support_xmax, _symin, _symax, _szmin, _szmax = support_extents
            target_right_x = support_xmin - MASK_JIG_GAP_TO_SUPPORT

    if target_right_x is None:
        return mask_jig_id

    dx = target_right_x - mask_xmax
    if abs(dx) > 1e-9:
        rs.MoveObject(mask_jig_id, (dx, 0.0, 0.0))
    return mask_jig_id


def main():
    validate_global_parameters()

    path = choose_dxf_path()
    if not path:
        print("Import annule.")
        return

    if CLEAR_DOCUMENT_BEFORE_IMPORT:
        clear_document()

    before_ids = set(rs.AllObjects() or [])
    ok = import_dxf(path)
    after_ids = set(rs.AllObjects() or [])
    new_ids = list(after_ids - before_ids)

    if not ok:
        print("Echec de l'import DXF:", path)
        return

    print("DXF importe:", path)
    print("Nouveaux objets:", len(new_ids))

    imported_opening_ids = filter_object_ids_by_layer(new_ids, OPENINGS_LAYER)
    imported_edgecut_ids = filter_object_ids_by_layer(new_ids, EDGE_CUTS_LAYER)

    if not rs.IsLayer(OPENINGS_LAYER):
        print("La couche '{}' est introuvable.".format(OPENINGS_LAYER))
        print("Couches disponibles:", ", ".join(rs.LayerNames() or []))
        return
    if not imported_opening_ids:
        print("Aucune ouverture importee trouvee sur la couche '{}' dans ce DXF.".format(OPENINGS_LAYER))
        return
    if not imported_edgecut_ids:
        print(
            "Aucun objet importe sur la couche '{}' dans ce DXF. "
            "Active l'export des EDGE_CUTS dans test_export_pads.py.".format(EDGE_CUTS_LAYER)
        )
        return

    outer_edgecut_id = None
    hinge_axis_id = None
    jig_axis_id = None
    jig_post_ids = []
    jig_plate_id = None
    jig_lever_id = None
    jig_hinge_clearance_cut_id = None
    jig_pocket_cut_id = None
    jig_openings_cut_ids = []
    jig_result_id = None
    hinge_body_id = None
    plate_parts = {}
    plate_result_id = None
    support_result_id = None
    mask_jig_result_id = None
    ejection_cut_id = None
    lever_cut_id = None
    pcb_seat_cut_id = None
    if rs.IsLayer(EDGE_CUTS_LAYER):
        outer_edgecut_id = find_largest_outer_edgecut(EDGE_CUTS_LAYER, imported_edgecut_ids)
        if outer_edgecut_id:
            validate_geometry_parameters(outer_edgecut_id)
            hide_other_edgecuts(EDGE_CUTS_LAYER, outer_edgecut_id, imported_edgecut_ids)
            style_outer_edgecut(outer_edgecut_id)
            hinge_axis_id = create_hinge_axis_from_outer_frame(outer_edgecut_id)
            jig_axis_id = create_jig_axis_from_outer_frame(outer_edgecut_id)
            jig_post_ids = create_jig_hinge_posts_from_outer_frame(outer_edgecut_id)
            jig_plate_id = create_jig_plate_from_outer_frame(outer_edgecut_id)
            jig_hinge_clearance_cut_id = create_jig_hinge_clearance_cut_from_outer_frame(outer_edgecut_id)
            jig_plate_id = subtract_hinge_clearance_from_jig_plate(jig_plate_id, jig_hinge_clearance_cut_id)
            jig_pocket_cut_id = create_jig_plate_pocket_from_outer_frame(outer_edgecut_id)
            jig_plate_id = subtract_hinge_clearance_from_jig_plate(jig_plate_id, jig_pocket_cut_id)
            jig_openings_cut_ids = create_openings_cutters_for_jig(imported_opening_ids)
            jig_plate_id = subtract_multiple_cutters_from_jig_plate(jig_plate_id, jig_openings_cut_ids)
            jig_lever_id = create_jig_lever_from_outer_frame(outer_edgecut_id)
            jig_result_id = union_jig_parts(jig_post_ids + [jig_plate_id, jig_lever_id])
            jig_result_id = subtract_jig_axis_from_result(jig_result_id, jig_axis_id)
            hinge_body_id = create_hinge_body_from_outer_frame(outer_edgecut_id)
            if hinge_axis_id and hinge_body_id:
                hinge_body_id = subtract_hinge_axis_from_body(hinge_body_id, hinge_axis_id)
            plate_parts = create_plate_solids_from_outer_frame(outer_edgecut_id)
            ensure_layer(PLATE_RESULT_LAYER, PLATE_RESULT_COLOR)
            plate_result_id = boolean_union_keep(
                [plate_parts.get("plate_1"), plate_parts.get("plate_2")],
                PLATE_RESULT_LAYER,
                PLATE_RESULT_COLOR,
            )
            plate_result_id = boolean_difference_keep(
                plate_result_id,
                plate_parts.get("plate_3"),
                PLATE_RESULT_LAYER,
                PLATE_RESULT_COLOR,
            )
            hide_objects(list(plate_parts.values()))
            ensure_layer(SUPPORT_RESULT_LAYER, SUPPORT_RESULT_COLOR)
            if hinge_body_id and plate_result_id:
                support_result_id = boolean_union_keep(
                    [hinge_body_id, plate_result_id],
                    SUPPORT_RESULT_LAYER,
                    SUPPORT_RESULT_COLOR,
                )
            if support_result_id:
                ejection_cut_id = create_ejection_cut_from_outer_frame(outer_edgecut_id)
                support_result_id = subtract_ejection_cut_from_support(support_result_id, ejection_cut_id)
            if support_result_id:
                lever_cut_id = create_lever_cut_from_outer_frame(outer_edgecut_id)
                support_result_id = subtract_lever_cut_from_support(support_result_id, lever_cut_id)
            if support_result_id:
                pcb_seat_cut_id = create_pcb_seat_cut_from_outer_frame(outer_edgecut_id)
                support_result_id = subtract_pcb_seat_cut_from_support(support_result_id, pcb_seat_cut_id)
            mask_jig_result_id = create_mask_jig_base_from_outer_frame(outer_edgecut_id)
            if mask_jig_result_id:
                mask_pocket_id = create_mask_jig_mask_pocket_from_outer_frame(outer_edgecut_id)
                mask_jig_result_id = boolean_difference_delete(
                    mask_jig_result_id,
                    mask_pocket_id,
                    MASK_JIG_RESULT_LAYER,
                    MASK_JIG_RESULT_COLOR,
                    "Echec de la soustraction de la poche masque.",
                )
            if mask_jig_result_id:
                pcb_cut_id = create_mask_jig_pcb_cut_from_outer_frame(outer_edgecut_id)
                mask_jig_result_id = boolean_difference_delete(
                    mask_jig_result_id,
                    pcb_cut_id,
                    MASK_JIG_RESULT_LAYER,
                    MASK_JIG_RESULT_COLOR,
                    "Echec de la soustraction du contour PCB dans le jig masque.",
                )
            if mask_jig_result_id:
                mask_ejection_cut_ids = create_mask_jig_ejection_cuts_from_outer_frame(outer_edgecut_id)
                mask_jig_result_id = subtract_cutters_from_mask_jig(mask_jig_result_id, mask_ejection_cut_ids)
                mask_jig_result_id = move_mask_jig_left_of_support(mask_jig_result_id, support_result_id)
            print("Cadre externe trouve sur '{}': {}".format(EDGE_CUTS_LAYER, outer_edgecut_id))
            if hinge_axis_id:
                print(
                    "Axe de charniere cree: Y = ymin + {:.3f}, Z = {:.3f}, diam = {:.3f}".format(
                        HINGE_AXIS_OFFSET_FROM_YMIN, HINGE_AXIS_Z, HINGE_AXIS_DIAMETER
                    )
                )
            if jig_axis_id:
                print(
                    "Axe du jig cree: Y = ymin + {:.3f}, Z = {:.3f}, diam = {:.3f}".format(
                        HINGE_AXIS_OFFSET_FROM_YMIN, HINGE_AXIS_Z, JIG_AXIS_DIAMETER
                    )
                )
            if jig_post_ids:
                print("Montants du jig crees: {}".format(len(jig_post_ids)))
            if jig_plate_id:
                print("Plateau du jig cree.")
            if jig_hinge_clearance_cut_id:
                print("Degagement de charniere soustrait du plateau du jig.")
            if jig_pocket_cut_id:
                print("Poche principale du plateau du jig creee.")
            if jig_openings_cut_ids:
                print("Openings soustraits du plateau du jig: {}".format(len(jig_openings_cut_ids)))
            if jig_lever_id:
                print("Levier du jig cree.")
            if jig_result_id:
                print("Jig final: union montants + plateau + levier, puis soustraction axe.")
            if hinge_body_id:
                print(
                    "Corps de charniere cree: largeur Y = {:.3f}, hauteur Z = {:.3f}, conge = {:.3f}".format(
                        HINGE_BODY_WIDTH_Y, HINGE_BODY_HEIGHT_Z, HINGE_BODY_FILLET_RADIUS
                    )
                )
            if plate_parts:
                print("Plateau: 3 extrusions creees.")
            if plate_result_id:
                print("Plateau: plate1 + plate2 - plate3 applique.")
            if support_result_id:
                print("Support final: union plateau + charniere appliquee.")
            if ejection_cut_id:
                print("Ouverture d'ejection soustraite du support.")
            if lever_cut_id:
                print("Decoupe de levier soustraite du support.")
            if pcb_seat_cut_id:
                print("Empreinte PCB soustraite du support.")
            if mask_jig_result_id:
                print("Jig masque de soudure cree et decale a gauche du support.")
        else:
            print(
                "Aucun cadre externe ferme trouve sur '{}'. "
                "Verifie que le DXF exporte bien un contour PCB ferme sur cette couche.".format(EDGE_CUTS_LAYER)
            )
    else:
        print("La couche '{}' est introuvable.".format(EDGE_CUTS_LAYER))

    opening_ids = imported_opening_ids
    final_result_ids = [obj_id for obj_id in [jig_result_id, support_result_id, mask_jig_result_id] if obj_id and rs.IsObject(obj_id)]
    if final_result_ids:
        cleanup_construction_geometry(
            final_result_ids + opening_ids,
            [OPENINGS_LAYER, JIG_RESULT_LAYER, SUPPORT_RESULT_LAYER, MASK_JIG_RESULT_LAYER],
        )
        delete_empty_layers([OPENINGS_LAYER, JIG_RESULT_LAYER, SUPPORT_RESULT_LAYER, MASK_JIG_RESULT_LAYER])
        set_layer_visibility(
            [
                OPENINGS_LAYER,
                JIG_RESULT_LAYER,
                SUPPORT_RESULT_LAYER,
                MASK_JIG_RESULT_LAYER,
            ],
            HIDE_OTHER_LAYERS,
        )
    else:
        print("Aucun objet final genere : nettoyage annule pour conserver la geometrie intermediaire.")
        set_layer_visibility(
            [
                OPENINGS_LAYER,
                EDGE_CUTS_LAYER,
                HINGE_AXIS_LAYER,
                JIG_AXIS_LAYER,
                JIG_POSTS_LAYER,
                JIG_PLATE_LAYER,
                JIG_HINGE_CLEARANCE_CUT_LAYER,
                JIG_POCKET_CUT_LAYER,
                JIG_OPENINGS_CUT_LAYER,
                JIG_LEVER_LAYER,
                JIG_RESULT_LAYER,
                HINGE_BODY_LAYER,
                PLATE_1_LAYER,
                PLATE_2_LAYER,
                PLATE_3_LAYER,
                PLATE_RESULT_LAYER,
                SUPPORT_RESULT_LAYER,
                EJECTION_CUT_LAYER,
                LEVER_CUT_LAYER,
                PCB_SEAT_CUT_LAYER,
                MASK_JIG_RESULT_LAYER,
            ],
            False,
        )
    zoom_ids = opening_ids
    if outer_edgecut_id:
        zoom_ids.append(outer_edgecut_id)
    if hinge_axis_id:
        zoom_ids.append(hinge_axis_id)
    if jig_axis_id:
        zoom_ids.append(jig_axis_id)
    if jig_result_id:
        zoom_ids.append(jig_result_id)
    else:
        zoom_ids.extend(jig_post_ids)
        if jig_plate_id:
            zoom_ids.append(jig_plate_id)
        if jig_lever_id:
            zoom_ids.append(jig_lever_id)
    if hinge_body_id:
        zoom_ids.append(hinge_body_id)
    if support_result_id:
        zoom_ids.append(support_result_id)
    if mask_jig_result_id:
        zoom_ids.append(mask_jig_result_id)
    elif plate_result_id:
        zoom_ids.append(plate_result_id)
    else:
        zoom_ids.extend([obj_id for obj_id in plate_parts.values() if obj_id])
    zoom_to_objects(zoom_ids)
    print(
        "Couches affichees: {}".format(
            ", ".join(
                [
                    OPENINGS_LAYER,
                    JIG_RESULT_LAYER,
                    SUPPORT_RESULT_LAYER,
                    MASK_JIG_RESULT_LAYER,
                ]
            )
        )
    )


if __name__ == "__main__":
    main()
