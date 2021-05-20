
/*
FEATURE_NAMES = [
    'area',
    'dist_closest',
    'dist_closest2',
    'num_addresses',
    'tax_amount',
    'land_value',
    'building_value',
    'land_value_per_area'
]
*/

const USE_AGNES_ROAD_POLY = true;
const USE_AGNES_CENTROID_LABELS = false;

const USE_HOUSE_FEATURE_COLORMAP = false;
const COLORMAP_FEATURE_USED = 'land_value';

const FORCE_BORING_COLOR = false;
const BORING_COLOR = '#000000';

const USE_ROAD_POLY = false;

const USE_GRID_OUTLINE = false;
const USE_CONVEX_HULL = false;
const USE_REAL_POINTS = false;
const DELETE_SINGLE_GRIDSQUARES = true;

let map;

function randrange(x) {
    return Math.floor(Math.random()*x);
}

function randColor() {
    let ans = '#';
    for (let i=0;i<6;i++) {
        ans += '0123456789ABCDEF'[randrange(16)];
    }
    return ans;
}

function convertPt(pt) {
    return {lat: pt[1], lng: pt[0]};
}

function convertPoly(pts) {
    return pts.map(pt => convertPt(pt));
}

function convertMultiPoly(ptss) {
    return ptss.map(pts => convertPoly(pts));
}

function displayPolys(polys) {
    polys.forEach(pp => {
        const col = FORCE_BORING_COLOR ? BORING_COLOR : randColor();
        const xline = new google.maps.Polygon({
            paths: convertMultiPoly(pp),
            strokeColor: col,
            strokeOpacity: 0.8,
            strokeWeight: 1,
            fillColor: col,
            fillOpacity: 0.2
        });
        xline.setMap(map);
    });
}

function displayMarkers(objs) {
    objs.forEach(obj => {
        new google.maps.Marker({
            position: convertPt(obj.point),
            label: obj.label,
            map: map,
        });
    });
}

function displayColoredCircles(objs, radius, opacity) {
    objs.forEach(obj => {
        const col = obj.color;
        const pt = obj.point;
        new google.maps.Circle({
            strokeColor: col,
            strokeOpacity: opacity,
            strokeWeight: 1,
            fillColor: col,
            fillOpacity: opacity,
            map: map,
            center: convertPt(pt),
            radius: radius
        });
    });
}



function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 40.1164, lng: -88.2434 },
        zoom: 13,
    });
    
    if (USE_ROAD_POLY) {
        displayPolys(road_regions);
    }
    
    if (USE_AGNES_ROAD_POLY) {
        displayPolys(agnes_road_regions);
    }
    
    if (USE_AGNES_CENTROID_LABELS) {
        displayMarkers(agnes_centroid_labels);
    }
    
    if (USE_HOUSE_FEATURE_COLORMAP) {
        displayColoredCircles(
            feature_color_map[COLORMAP_FEATURE_USED],
            radius=20, opacity=.5
        );
    }
    
    /*
    const NUM = hulls.length;
    for (let index=0;index<NUM;index++) {
        const col = randColor();
        const hull = hulls[index];
        const comp = components[index];
        const outline = outlines[index];
        
        if (USE_GRID_OUTLINE) {
            outline.forEach(ol => {
                let olpath = convertPoly(ol[0]);
                if (DELETE_SINGLE_GRIDSQUARES && olpath.length==5) return;
                const olline = new google.maps.Polygon({
                    path: olpath,
                    strokeColor: col,
                    strokeOpacity: 1.0,
                    strokeWeight: 1,
                    fillColor: col,
                    fillOpacity: 0.2
                });
                olline.setMap(map);
            });
        }
        
        if (USE_CONVEX_HULL) {
            let path = convertPoly(hull);
            const pline = new google.maps.Polygon({
                path: path,
                strokeColor: col,
                strokeOpacity: 1.0,
                strokeWeight: 1,
                fillColor: col,
                fillOpacity: 0.2
            });
            pline.setMap(map);
        }
        
        if (USE_REAL_POINTS) {
            comp.forEach(pt => {
                const circ = new google.maps.Circle({
                    strokeColor: col,
                    strokeOpacity: 0.8,
                    strokeWeight: 1,
                    fillColor: col,
                    fillOpacity: 0.35,
                    map,
                    center: convertPt(pt),
                    radius: 1
                });
            });
        }
    }
    */
}
