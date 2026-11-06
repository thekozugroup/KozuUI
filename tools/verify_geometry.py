"""Read-only FigCraft geometry guardrail. Run --self-test or pass a .figcraft file."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

TOLERANCE = 0.5
STATE_NAME = re.compile(r'\b(active|focus(?:ed)?|selected|pressed|checked|mixed)\b', re.I)
UNSELECTED_MARK = re.compile(r'^(checkbox|radio)\s*/\s*(unchecked|unselected|off|default|rest)\b', re.I)

def layers(value, ancestors=()):
    if isinstance(value, dict):
        if 'id' in value and 'type' in value:
            yield value, ancestors
            ancestors += (value,)
        for key in ('pages', 'children'):
            for child in value.get(key, []):
                yield from layers(child, ancestors)

def radii(layer):
    value = layer.get('cornerRadius', 0)
    return [float(value)] * 4 if isinstance(value, (int, float)) else list(value)

def paired_icon_issues(slot, parent):
    labels = [child for child in parent.get('children', []) if child.get('type') == 'TEXT']
    if not labels:
        return []  # Icon-only controls keep their independent sizing rules.
    prefix = f"{slot['id']} {slot['name']} in {parent['id']} {parent.get('name')}"
    if (len(labels) != 1 or labels[0].get('leadingTrim') != 'capHeight'
            or any(c in labels[0].get('characters', '') for c in '\n\r\u2028\u2029')
            or labels[0].get('height', 0) <= 0):
        return [f"{prefix}: paired icon needs one single-line capHeight-trimmed label"]
    issues = []
    width, height = parent.get('width', 0), parent.get('height', 0)
    x, y = slot.get('x', 0), slot.get('y', 0)
    end_x = min((0, width-height), key=lambda end: abs(x-end))
    if (height <= 0 or abs(slot.get('width', 0)-height) > TOLERANCE
            or abs(slot.get('height', 0)-height) > TOLERANCE
            or abs(y) > TOLERANCE or abs(x-end_x) > TOLERANCE):
        issues.append(f"{prefix}: slot must be {height:g} square at (0, 0) or ({width-height:g}, 0)")
    parent_bounds = parent.get('absoluteBounds')
    if not parent_bounds:
        return issues + [f"{prefix}: parent absoluteBounds are required for visible-ink measurement"]
    ink = []
    for leaf, ancestors in layers(slot):
        if leaf.get('children') or leaf.get('type') not in ('VECTOR', 'LINE', 'RECTANGLE', 'ELLIPSE', 'POLYGON', 'STAR', 'FRAME'):
            continue
        if any(not node.get('visible', True) or node.get('opacity', 1) <= 0 for node in (*ancestors, leaf)):
            continue
        has_stroke = leaf.get('strokeWeight', 0) > 0 and any(
            paint.get('visible', True) and paint.get('opacity', 1) > 0
            for paint in leaf.get('strokes', []))
        stroke = (leaf['strokeWeight'] * {'inside':0, 'outside':1}.get(leaf.get('strokeAlign'), 0.5)
                  if has_stroke else 0)
        if not has_stroke and not any(paint.get('visible', True) and paint.get('opacity', 1) > 0
                                      for paint in leaf.get('fills', [])):
            continue
        bounds = leaf.get('absoluteBounds')
        if not bounds:
            issues.append(f"{prefix}: icon leaf {leaf['id']} has no absoluteBounds")
            continue
        ink.append((bounds['x']-stroke, bounds['y']-stroke,
                    bounds['x']+bounds['width']+stroke, bounds['y']+bounds['height']+stroke))
    if not ink:
        return issues + [f"{prefix}: no visible icon leaf geometry"]
    left, top = min(box[0] for box in ink), min(box[1] for box in ink)
    right, bottom = max(box[2] for box in ink), max(box[3] for box in ink)
    cap_height = labels[0]['height']
    if abs(bottom-top-cap_height) > TOLERANCE:
        issues.append(f"{prefix}: visible icon ink height {bottom-top:g}, expected label cap height {cap_height:g}")
    cx, cy = (left+right)/2, (top+bottom)/2
    ex, ey = parent_bounds['x']+end_x+height/2, parent_bounds['y']+height/2
    if abs(cx-ex) > TOLERANCE or abs(cy-ey) > TOLERANCE:
        issues.append(f"{prefix}: visible icon ink center ({cx:g}, {cy:g}), expected endcap center ({ex:g}, {ey:g})")
    return issues

def geometry_issues(document):
    issues = []
    for layer, ancestors in layers(document):
        name = layer.get('name', '')
        context = (*ancestors, layer)
        state_surface = False
        for node in context:
            if node.get('type') == 'PAGE':
                continue
            if UNSELECTED_MARK.match(node.get('name', '')):
                state_surface = False
            elif STATE_NAME.search(node.get('name', '')):
                state_surface = True
        glyph = layer.get('type') in ('VECTOR', 'LINE', 'TEXT') or any(
            node.get('name', '').lower().startswith(('aria /', 'lucide /', 'icon /', 'glyph /'))
            for node in context)
        if re.match(r'^focus ring\b', name, re.I):
            issues.append(f"{layer['id']} {name}: legacy focus-ring layer is not allowed")
        elif state_surface and not glyph and layer.get('strokeWeight', 1) > 0 and any(
                paint.get('visible', True) and paint.get('opacity', 1) > 0
                for paint in layer.get('strokes', [])):
            issues.append(f"{layer['id']} {name}: state surface must not have an outer border stroke")
        if not ancestors:
            continue
        parent = ancestors[-1]
        if name == 'Icon slot / concentric endcap':
            issues.extend(paired_icon_issues(layer, parent))
        x, y = layer.get('x', 0), layer.get('y', 0)
        width, height = layer.get('width', 0), layer.get('height', 0)
        pw, ph = parent.get('width', 0), parent.get('height', 0)
        inner, outer = radii(layer), radii(parent)
        gaps = [(x, y), (pw-x-width, y), (pw-x-width, ph-y-height), (x, ph-y-height)]
        corner_action = any(annotation.get('label', '').startswith('[corner-action]')
                            for annotation in layer.get('annotations', []))
        if corner_action:
            right, bottom = gaps[2]
            if abs(right-bottom) > TOLERANCE:
                issues.append(f"{layer['id']} {name}: corner action insets {right:g} right, {bottom:g} bottom must be equal")
            expected = inner[2]+right
            if abs(outer[2]-expected) > TOLERANCE:
                issues.append(f"{layer['id']} {name}: parent {parent['id']} bottom-right radius {outer[2]:g}, expected action radius + inset {expected:g}")
        for corner, (horizontal, vertical) in enumerate(gaps):
            if corner_action and corner == 2:
                continue  # The explicit corner-action check also covers independent controls.
            # Adjacent rounded edges with a uniform inset must share a corner center.
            # Independent circular controls are not curved insets of their cards.
            independent_circle = name.startswith(('Avatar /', 'Icon button /', 'Rail item /', 'Selected check'))
            if independent_circle or inner[corner] <= 0 or outer[corner] <= 0:
                continue
            if min(horizontal, vertical) < 0 or abs(horizontal-vertical) > TOLERANCE:
                continue
            if horizontal > 24 or horizontal >= outer[corner]:
                continue
            expected = max(0, outer[corner]-horizontal)
            if abs(inner[corner]-expected) > TOLERANCE:
                issues.append(f"{layer['id']} {layer.get('name')}: corner {corner} radius {inner[corner]}, expected {expected}")

        if name.startswith('Toolbar /'):
            items = [child for child in layer.get('children', [])
                     if any(c.get('name', '').startswith('Aria /') for c in child.get('children', []))]
            if items:
                left = min(child['x'] for child in items)
                right = width-max(child['x']+child['width'] for child in items)
                if abs(left-right) > TOLERANCE:
                    issues.append(f"{layer['id']} {name}: toolbar padding {left} left, {right} right")
                if any(abs(r-min(width,height)/2) > TOLERANCE for r in inner):
                    issues.append(f"{layer['id']} {name}: capsule radius must equal half its shorter dimension")

        rail_item = name.startswith('Rail item /')
        if rail_item:
            if abs(width-height) > TOLERANCE or any(abs(r-width/2) > TOLERANCE for r in inner):
                issues.append(f"{layer['id']} {name}: rail target must be circular")
            if parent.get('name') == 'Navigation / side rail' and abs(x+width/2-pw/2) > TOLERANCE:
                issues.append(f"{layer['id']} {name}: target is not centered in the rail")
        icon_only_parent = parent.get('name', '').startswith(('Icon button /', 'Rail item /', 'Checkbox /')) or parent.get('name') in ('Back to schedule', 'More workspace actions', 'Selection visual')
        toolbar_item = any(a.get('name', '').startswith('Toolbar /') for a in ancestors[-2:])
        if name.startswith('Aria /') and (icon_only_parent or toolbar_item):
            if abs(x+width/2-pw/2) > TOLERANCE or abs(y+height/2-ph/2) > TOLERANCE:
                issues.append(f"{layer['id']} {name}: icon is not centered in its target")
        # Older rail compositions placed icons beside the selection shape.
        legacy_rail = parent.get('name') == 'Navigation / side rail' or (
            parent.get('name', '').startswith('Adaptive task /') and pw < 840)
        if name.startswith('Aria /') and legacy_rail and x < 100:
            issues.append(f"{layer['id']} {name}: rail icon needs an explicit centered circular target")

        is_button = (any(s in name.lower() for s in ('button /','state=','capsule','/ action /','native text button','resume featured film','wearables / list / selected'))
                     or any(c.get('name') == 'Icon slot / concentric endcap' for c in layer.get('children', [])))
        compact_scroll_row = name.startswith('Transforming row /') and height <= 44
        if (is_button or compact_scroll_row or name.startswith(('Avatar /', 'Chip /'))) and height <= 110:
            for child in layer.get('children', []):
                if child.get('type') == 'TEXT':
                    cx = child.get('x',0)+child.get('width',0)/2
                    cy = child.get('y',0)+child.get('height',0)/2
                    if abs(cx-width/2)>TOLERANCE or abs(cy-height/2)>TOLERANCE:
                        issues.append(f"{layer['id']} {name}: button label is not centered")
    return issues

def read_document(cli, path):
    process = subprocess.Popen([cli, 'mcp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True)
    request_id = 0
    def rpc(method, params):
        nonlocal request_id
        request_id += 1
        process.stdin.write(json.dumps({'jsonrpc':'2.0', 'id':request_id, 'method':method, 'params':params})+'\n')
        process.stdin.flush()
        while True:
            line = process.stdout.readline()
            if not line:
                raise RuntimeError('FigCraft MCP stopped before replying')
            reply = json.loads(line)
            if reply.get('id') == request_id:
                if 'error' in reply:
                    raise RuntimeError(reply['error'])
                return reply['result']
    def tool(name, arguments):
        result = rpc('tools/call', {'name':name, 'arguments':arguments})
        if result.get('isError'):
            raise RuntimeError(result)
        return json.loads('\n'.join(x['text'] for x in result['content'] if x['type']=='text'))
    try:
        rpc('initialize', {'protocolVersion':'2025-06-18', 'capabilities':{}, 'clientInfo':{'name':'Kozu geometry check','version':'1.0'}})
        tool('open_file', {'path':str(path.resolve())})
        document = tool('inspect_document', {'allPages':True, 'depth':20, 'maxBytes':30000000})
        def expand(layer):
            # Reparented subtrees can be abbreviated by the document inspector.
            if layer.get('childCount', 0) > len(layer.get('children', [])):
                layer.update(tool('get_node', {'id':layer['id'], 'depth':20}))
            for child in layer.get('pages', layer.get('children', [])):
                expand(child)
        expand(document)
        return document
    finally:
        process.terminate()
        process.wait(timeout=10)

def self_test():
    child = {'id':2, 'type':'FRAME', 'name':'Nested surface', 'x':16, 'y':16, 'width':168, 'height':168, 'cornerRadius':24}
    parent = {'id':1, 'type':'FRAME', 'name':'Container', 'width':200, 'height':200, 'cornerRadius':40, 'children':[child]}
    assert not geometry_issues(parent)
    child['cornerRadius'] = 25
    assert geometry_issues(parent)
    child['cornerRadius'] = 24
    assert max(0, 16-24) == 0
    icon = {'id':4, 'type':'FRAME', 'name':'Aria / lucide:plus', 'x':12, 'y':12, 'width':24, 'height':24}
    target = {'id':3, 'type':'FRAME', 'name':'Icon button / plus', 'x':8, 'y':8, 'width':48, 'height':48, 'cornerRadius':24, 'children':[icon]}
    toolbar = {'id':5, 'type':'FRAME', 'name':'Toolbar / test', 'width':64, 'height':64, 'cornerRadius':32, 'children':[target]}
    document={'pages':[{'id':0,'type':'PAGE','children':[toolbar]}]}
    assert not geometry_issues(document)
    toolbar['width']=72
    assert geometry_issues(document)
    toolbar['width']=64; icon['x']=13
    assert geometry_issues(document)
    ring = {'id':7, 'type':'RECTANGLE', 'name':'Focus ring / test', 'x':-5,'y':-5,'width':210,'height':58,'cornerRadius':29}
    control = {'id':6, 'type':'FRAME','name':'Control','width':200,'height':48,'cornerRadius':24,'children':[ring]}
    assert any('legacy focus-ring' in issue for issue in geometry_issues(control))
    assert any('legacy focus-ring' in issue for issue in geometry_issues(ring))
    control['children'] = []
    control.update(strokeWeight=2, strokes=[{'type':'solid', 'color':'#FFFFFF'}])
    for state in ('Active', 'Focus', 'Focused', 'Selected', 'Pressed', 'Checked', 'Mixed'):
        control['name'] = f'State={state}'
        assert any('outer border stroke' in issue for issue in geometry_issues(control)), state
    control.update(name='State=Focus', strokes=[])
    surface = {'id':10, 'type':'RECTANGLE', 'name':'Surface', 'width':200, 'height':48,
               'cornerRadius':24, 'strokeWeight':2, 'strokes':[{'type':'solid', 'color':'#FFFFFF'}]}
    control['children'] = [surface]
    assert any('10 Surface: state surface' in issue for issue in geometry_issues(control))
    surface['strokes'] = []
    assert not geometry_issues(control)
    glyph_outline = {'id':12, 'type':'ELLIPSE', 'name':'Circle', 'x':2, 'y':2, 'width':20, 'height':20,
                     'strokeWeight':1.8, 'strokes':[{'type':'solid', 'color':'#FFFFFF'}]}
    glyph = {'id':11, 'type':'FRAME', 'name':'Aria / lucide:circle', 'x':16, 'y':12,
             'width':24, 'height':24, 'children':[glyph_outline]}
    control['children'] = [glyph]
    assert not geometry_issues(control)
    glyph['name'] = 'Icon / custom'
    assert not geometry_issues(control)
    glyph['name'] = 'Custom glyph'
    glyph_outline.update(type='VECTOR', name='Vector')
    assert not geometry_issues(control)
    for mark, kind in (('Checkbox', 'RECTANGLE'), ('Radio', 'ELLIPSE')):
        outline = {'id':13, 'type':kind, 'name':f'{mark} / unchecked', 'x':16, 'y':8,
                   'width':32, 'height':32, 'strokeWeight':1.8,
                   'strokes':[{'type':'solid', 'color':'#64748B'}]}
        control['children'] = [outline]
        assert not geometry_issues(control), mark
        outline['name'] = f'{mark} / checked'
        assert any('outer border stroke' in issue for issue in geometry_issues(control)), mark
    badge = {'id':14, 'type':'FRAME', 'name':'Selected check', 'x':244, 'y':12,
             'width':44, 'height':44, 'cornerRadius':22}
    card = {'id':15, 'type':'FRAME', 'name':'TV / Full-bleed card / selected',
            'width':300, 'height':168.75, 'cornerRadius':20, 'children':[badge]}
    assert not geometry_issues(card)
    badge.update(strokeWeight=2, strokes=[{'type':'solid', 'color':'#FFFFFF'}])
    assert any('outer border stroke' in issue for issue in geometry_issues(card))
    icon['x']=12
    target.update(name='Rail item / test', x=8, y=8)
    rail_fixture={'id':0,'type':'PAGE','children':[target]}
    assert not geometry_issues(rail_fixture)
    icon['x']=6
    assert any('not centered' in issue for issue in geometry_issues(rail_fixture))
    icon['x']=12; target['width']=56
    assert any('circular' in issue for issue in geometry_issues(rail_fixture))
    target.update(x=120, y=120, height=56, cornerRadius=28)
    icon.update(x=16, y=16)
    independent={'id':0,'type':'FRAME','name':'Card','width':200,'height':200,'cornerRadius':28,'children':[target]}
    assert not geometry_issues(independent)
    corner_target = {'id':30, 'type':'FRAME', 'name':'Icon button / corner', 'x':136, 'y':96,
                     'width':48, 'height':48, 'cornerRadius':24,
                     'annotations':[{'label':'[corner-action] Bottom-right anchor'}]}
    corner_card = {'id':31, 'type':'FRAME', 'name':'Card', 'width':200, 'height':160,
                   'cornerRadius':40, 'children':[corner_target]}
    assert not geometry_issues(corner_card)
    corner_target['y'] = 94
    assert any('corner action insets' in issue for issue in geometry_issues(corner_card))
    corner_target['y'] = 96
    corner_card['cornerRadius'] = [5, 6, 39, 7]
    assert any('bottom-right radius' in issue for issue in geometry_issues(corner_card))
    corner_card['cornerRadius'] = [5, 6, 40, 7]
    assert not geometry_issues(corner_card)
    corner_target.update(name='Button / corner', width=100, x=84, cornerRadius=12)
    corner_card['cornerRadius'] = [5, 6, 28, 7]
    assert not geometry_issues(corner_card)
    corner_target['cornerRadius'] = [1, 2, 11, 3]
    assert any('bottom-right radius' in issue for issue in geometry_issues(corner_card))
    corner_target.update(name='Icon button / unmarked', width=48, x=135, y=94, cornerRadius=24,
                         annotations=[{'description':'[corner-action] This is not an annotation label'}],
                         description='[corner-action] Component description is not the marker')
    assert not geometry_issues(corner_card)
    corner_target['annotations'] = [{'label':'Notes: [corner-action] is not a prefix'}]
    assert not geometry_issues(corner_card)
    label={'id':9,'type':'TEXT','name':'Pause','x':111,'y':16,'width':54,'height':24}
    capsule={'id':8,'type':'COMPONENT','name':'Wearables / Apple / Capsule primary','width':240,'height':56,'children':[label]}
    button_fixture={'id':0,'type':'PAGE','children':[capsule]}
    assert any('button label' in issue for issue in geometry_issues(button_fixture))
    label.update(x=48, width=144)
    assert not geometry_issues(button_fixture)
    paired_label = {'id':23, 'type':'TEXT', 'name':'Save', 'characters':'Save', 'leadingTrim':'capHeight',
                    'x':40, 'y':16, 'width':120, 'height':16}
    leaves = [
        {'id':24, 'type':'VECTOR', 'name':'Upper stroke', 'strokeWeight':2,
         'strokes':[{'type':'solid', 'color':'#FFFFFF'}],
         'absoluteBounds':{'x':119, 'y':217, 'width':10, 'height':5}},
        {'id':25, 'type':'VECTOR', 'name':'Lower stroke', 'strokeWeight':2,
         'strokes':[{'type':'solid', 'color':'#FFFFFF'}],
         'absoluteBounds':{'x':119, 'y':226, 'width':10, 'height':5}}]
    paired_slot = {'id':22, 'type':'FRAME', 'name':'Icon slot / concentric endcap',
                   'x':0, 'y':0, 'width':48, 'height':48, 'children':leaves}
    paired_button = {'id':21, 'type':'FRAME', 'name':'Button / paired', 'width':200, 'height':48,
                     'absoluteBounds':{'x':100, 'y':200, 'width':200, 'height':48},
                     'children':[paired_slot, paired_label]}
    assert not geometry_issues(paired_button)
    leaves[0]['absoluteBounds']['y'] -= 1
    leaves[1]['absoluteBounds']['y'] += 1
    assert any('ink height' in issue for issue in geometry_issues(paired_button))
    assert not any('ink center' in issue for issue in geometry_issues(paired_button))
    leaves[0]['absoluteBounds']['y'] += 1
    leaves[1]['absoluteBounds']['y'] -= 1
    for axis in ('x', 'y'):
        for leaf in leaves:
            leaf['absoluteBounds'][axis] += 1
        assert any('ink center' in issue for issue in geometry_issues(paired_button)), axis
        assert not any('ink height' in issue for issue in geometry_issues(paired_button)), axis
        for leaf in leaves:
            leaf['absoluteBounds'][axis] -= 1
    paired_slot['width'] = 47
    assert any('slot must be' in issue for issue in geometry_issues(paired_button))
    paired_slot.update(width=48, x=1)
    assert any('slot must be' in issue for issue in geometry_issues(paired_button))
    paired_slot.update(x=0, y=1)
    assert any('slot must be' in issue for issue in geometry_issues(paired_button))
    paired_slot.update(y=0, x=152)
    for leaf in leaves:
        leaf['absoluteBounds']['x'] += 152
    assert not geometry_issues(paired_button)
    hidden = {'id':26, 'type':'VECTOR', 'name':'Hidden geometry', 'visible':False,
              'strokes':[{'type':'solid', 'color':'#FFFFFF'}], 'strokeWeight':2,
              'absoluteBounds':{'x':0, 'y':0, 'width':1000, 'height':1000}}
    paired_slot['children'].append(hidden)
    assert not geometry_issues(paired_button)
    pause_bars = [
        {'id':27, 'type':'FRAME', 'name':'Pause bar', 'width':4, 'height':16,
         'fills':[{'type':'solid', 'color':'#FFFFFF'}],
         'absoluteBounds':{'x':270, 'y':216, 'width':4, 'height':16}},
        {'id':28, 'type':'FRAME', 'name':'Pause bar', 'width':4, 'height':16,
         'fills':[{'type':'solid', 'color':'#FFFFFF'}],
         'absoluteBounds':{'x':278, 'y':216, 'width':4, 'height':16}}]
    paired_slot['children'] = pause_bars
    assert not geometry_issues(paired_button)
    pause_bars[0]['absoluteBounds'].update(y=215, height=18)
    assert any('ink height' in issue for issue in geometry_issues(paired_button))
    assert not any('ink center' in issue for issue in geometry_issues(paired_button))
    pause_bars[0]['absoluteBounds'].update(y=216, height=16)
    for bar in pause_bars:
        bar['absoluteBounds']['x'] += 1
    assert any('ink center' in issue for issue in geometry_issues(paired_button))
    rotated_line = {'id':29, 'type':'LINE', 'name':'Rotated stroke', 'rotation':45,
                    'width':19.8, 'height':0, 'strokeWeight':2,
                    'strokes':[{'type':'solid', 'color':'#FFFFFF'}],
                    'absoluteBounds':{'x':269, 'y':217, 'width':14, 'height':14}}
    paired_slot['children'] = [rotated_line]
    assert not geometry_issues(paired_button)
    rotated_line['absoluteBounds'].update(y=216, height=16)
    assert any('ink height' in issue for issue in geometry_issues(paired_button))
    aligned_outline = {'id':32, 'type':'RECTANGLE', 'name':'Outlined glyph',
                       'strokeWeight':2, 'strokeAlign':'inside',
                       'strokes':[{'type':'solid', 'color':'#FFFFFF'}],
                       'absoluteBounds':{'x':272, 'y':216, 'width':8, 'height':16}}
    paired_slot['children'] = [aligned_outline]
    assert not geometry_issues(paired_button)
    aligned_outline['strokeAlign'] = 'outside'
    assert any('ink height' in issue for issue in geometry_issues(paired_button))
    assert not any('ink center' in issue for issue in geometry_issues(paired_button))
    aligned_outline['absoluteBounds'].update(x=274, y=218, width=4, height=12)
    assert not geometry_issues(paired_button)
    aligned_outline['strokeAlign'] = 'center'
    assert any('ink height' in issue for issue in geometry_issues(paired_button))
    aligned_outline['absoluteBounds'].update(x=273, y=217, width=6, height=14)
    assert not geometry_issues(paired_button)
    paired_slot['children'] = leaves
    paired_label['leadingTrim'] = 'none'
    assert any('capHeight-trimmed label' in issue for issue in geometry_issues(paired_button))
    paired_label.update(leadingTrim='capHeight', characters='Save\nnow')
    assert any('single-line' in issue for issue in geometry_issues(paired_button))
    paired_label['characters'] = 'Save'
    paired_button['children'] = [paired_slot]
    paired_slot['width'] = 24
    assert not geometry_issues(paired_button)
    paired_button['children'] = [paired_slot, paired_label]
    paired_slot['name'] = 'Row icon'
    assert not geometry_issues(paired_button)
    print('Geometry guardrail self-test passed')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='?', type=Path, default=Path(__file__).parents[1]/'Kozu Universal UI Kit.figcraft')
    parser.add_argument('--cli', default=shutil.which('figcraft-cli') or str(Path.home()/'Developer/Tools/figcraft/figcraft-cli-0.15.1-macos-universal/figcraft-cli'))
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        failures = geometry_issues(read_document(args.cli, args.file))
        print(json.dumps({'passed':not failures, 'issues':failures}, indent=2))
        raise SystemExit(bool(failures))
