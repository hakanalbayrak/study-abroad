#!/usr/bin/env python3
"""
Generate data/universities.js from use.csv
Usage: python3 scripts/generate-universities.py /path/to/use.csv
Run from repo root. Output goes to data/universities.js
"""

import csv, json, re, sys, os

FLAGS = {
    "Australia":"🇦🇺","Austria":"🇦🇹","Belgium":"🇧🇪","Canada":"🇨🇦",
    "Cyprus":"🇨🇾","Czech Republic":"🇨🇿","Denmark":"🇩🇰","Finland":"🇫🇮",
    "France":"🇫🇷","Georgia":"🇬🇪","Germany":"🇩🇪","Hungary":"🇭🇺",
    "Ireland":"🇮🇪","Italy":"🇮🇹","Latvia":"🇱🇻","Lithuania":"🇱🇹",
    "Malta":"🇲🇹","Netherlands":"🇳🇱","Poland":"🇵🇱","Spain":"🇪🇸",
    "Switzerland":"🇨🇭","Turkey":"🇹🇷","United Arab Emirates":"🇦🇪",
    "United Kingdom":"🇬🇧","United States":"🇺🇸",
}

# (uni_name_in_csv, country) → {city, lat, lng}
CAMPUS_COORDS = {
    ("Constructor (Jacobs) University, Bremen","Germany"):         {"city":"Bremen","lat":53.1688182,"lng":8.6501056},
    ("Royal Holloway University of London","United Kingdom"):      {"city":"Egham, Surrey","lat":51.4247097,"lng":-0.5667494},
    ("GBS Malta","Malta"):                                         {"city":"Valletta","lat":35.9042,"lng":14.5189},
    ("Charles University","Czech Republic"):                       {"city":"Prague","lat":50.0880,"lng":14.4208},
    ("Budapest Corvinus University","Hungary"):                    {"city":"Budapest","lat":47.4826,"lng":19.0571},
    ("EU Business School - Barcelona Campus","Spain"):             {"city":"Barcelona","lat":41.3851,"lng":2.1734},
    ("Florida International University","United States"):          {"city":"Miami, FL","lat":25.7571,"lng":-80.3729},
    ("Twente University - Pathway College","Netherlands"):         {"city":"Enschede","lat":52.2388,"lng":6.8558},
    ("SRH University - Berlin Campus","Germany"):                  {"city":"Berlin","lat":52.5034,"lng":13.3319},
    ("SRH University - Heidelberg Campus","Germany"):              {"city":"Heidelberg","lat":49.4074,"lng":8.7028},
    ("SRH University - Hamburg Campus","Germany"):                 {"city":"Hamburg","lat":53.5535,"lng":9.9937},
    ("SRH University - Stuttgart Campus","Germany"):               {"city":"Stuttgart","lat":48.7758,"lng":9.1829},
    ("SRH University - Dresden Campus","Germany"):                 {"city":"Dresden","lat":51.0504,"lng":13.7373},
    ("IU - International University of Applied Sciences","Germany"):{"city":"Erfurt","lat":50.9848,"lng":11.0299},
    ("GISMA University Berlin","Germany"):                         {"city":"Berlin","lat":52.5200,"lng":13.4050},
    ("Berlin School of Business and Innovation(BSBI)","Germany"):  {"city":"Berlin","lat":52.5009,"lng":13.3955},
    ("Aarhus University","Denmark"):                               {"city":"Aarhus","lat":56.1629,"lng":10.2039},
    ("Dublin City University","Ireland"):                          {"city":"Dublin","lat":53.3858,"lng":-6.2563},
    ("Trinity College Dublin","Ireland"):                          {"city":"Dublin","lat":53.3439,"lng":-6.2546},
    ("University College Dublin","Ireland"):                       {"city":"Dublin","lat":53.3085,"lng":-6.2248},
    ("Northeastern University London","United Kingdom"):           {"city":"London","lat":51.5194,"lng":-0.0846},
    ("Coventry University","United Kingdom"):                      {"city":"Coventry","lat":52.4079,"lng":-1.5080},
    ("University of Birmingham","United Kingdom"):                 {"city":"Birmingham","lat":52.4510,"lng":-1.9307},
    ("University of Bristol","United Kingdom"):                    {"city":"Bristol","lat":51.4588,"lng":-2.6031},
    ("University of Sussex","United Kingdom"):                     {"city":"Brighton","lat":50.8671,"lng":-0.0861},
    ("Swansea University","United Kingdom"):                       {"city":"Swansea","lat":51.6157,"lng":-3.9775},
    ("GBS Dubai","United Arab Emirates"):                          {"city":"Dubai","lat":25.1972,"lng":55.2744},
    ("Rochester Institute of Technology of Dubai (RIT Dubai)","United Arab Emirates"):{"city":"Dubai","lat":25.1125,"lng":55.1393},
    ("Griffith University","Australia"):                           {"city":"Gold Coast","lat":-28.0020,"lng":153.4300},
    ("University of Adelaide","Australia"):                        {"city":"Adelaide","lat":-34.9207,"lng":138.6047},
    ("Western Sydney University","Australia"):                     {"city":"Penrith","lat":-33.7573,"lng":150.7007},
    # EAE split (see SPLIT_UNIS below)
    ("EAE Business School (Madrid)","Spain"):                      {"city":"Madrid","lat":40.4168,"lng":-3.7038},
    ("EAE Business School (Barcelona)","Spain"):                   {"city":"Barcelona","lat":41.3851,"lng":2.1734},
    # TBS split
    ("Toulouse Business School (TBS) - Toulouse","France"):        {"city":"Toulouse","lat":43.6047,"lng":1.4442},
    ("Toulouse Business School (TBS) - Paris","France"):           {"city":"Paris","lat":48.8566,"lng":2.3522},
}

# Entries in CSV that need to be split into multiple cities
SPLIT_UNIS = {
    ("EAE Business School (Madrid and Barcelona)","Spain"): [
        "EAE Business School (Madrid)",
        "EAE Business School (Barcelona)",
    ],
    ("Toulouse Business School (TBS) - Toulouse and Paris","France"): [
        "Toulouse Business School (TBS) - Toulouse",
        "Toulouse Business School (TBS) - Paris",
    ],
}

# Manual entries not in CSV (kept from original app)
MANUAL_UNIS = [
    {
        "id":"queen-mary-london-gb",
        "flag":"🇬🇧","country":"United Kingdom","uni":"Queen Mary University of London","city":"London",
        "campus":{"lat":51.5237113,"lng":-0.040729},
        "programs":[
            {"name":"Law","domain":"Law","level":"Bachelor's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"3","appFee":0,"notes":""},
            {"name":"Engineering","domain":"Engineering","level":"Bachelor's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"3","appFee":0,"notes":""},
            {"name":"Computer Science","domain":"Computer/IT","level":"Bachelor's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"3","appFee":0,"notes":""},
            {"name":"Business Management","domain":"Business","level":"Bachelor's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"3","appFee":0,"notes":""},
            {"name":"Medicine","domain":"Medicine","level":"Bachelor's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"5","appFee":0,"notes":""},
            {"name":"Dentistry","domain":"Dentistry","level":"Bachelor's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"5","appFee":0,"notes":""},
            {"name":"Artificial Intelligence","domain":"Computer/IT","level":"Master's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"1","appFee":0,"notes":""},
            {"name":"Banking & Finance","domain":"Finance","level":"Master's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"1","appFee":0,"notes":""},
            {"name":"International Commercial Law","domain":"Law","level":"Master's Degree","feeUSD":0,"requirements":"","deadline":"","duration":"1","appFee":0,"notes":""},
        ]
    }
]

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def make_id(uni, country):
    cc = {"United Kingdom":"gb","United States":"us","United Arab Emirates":"ae",
          "Czech Republic":"cz","Germany":"de","France":"fr","Spain":"es",
          "Hungary":"hu","Netherlands":"nl","Ireland":"ie","Italy":"it",
          "Australia":"au","Canada":"ca","Malta":"mt","Denmark":"dk",
          "Finland":"fi","Georgia":"ge","Austria":"at","Belgium":"be",
          "Latvia":"lv","Lithuania":"lt","Poland":"pl","Switzerland":"ch",
          "Cyprus":"cy","Turkey":"tr"}.get(country, slugify(country)[:2])
    return slugify(uni)[:40] + '-' + cc

def parse_fee(s):
    try:
        return int(float(s.replace(',','')))
    except:
        return 0

def level_bucket(level):
    l = level.lower()
    if "bachelor" in l: return "ug"
    if "master" in l or "graduate cert" in l or "graduate dip" in l: return "pg"
    return "other"

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Downloads/use.csv")
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'universities.js')
    out_path = os.path.normpath(out_path)

    with open(csv_path, encoding='utf-8') as f:
        f.readline()  # skip "Data Export" header
        reader = csv.DictReader(f)
        rows = list(reader)

    # Group programs by (uni_name, country)
    groups = {}
    for r in rows:
        key = (r['University Name'].strip(), r['Country Name'].strip())
        if key not in groups:
            groups[key] = []
        groups[key].append(r)

    unis = []

    for (uni_name, country), programs in sorted(groups.items(), key=lambda x: (x[0][1], x[0][0])):
        split = SPLIT_UNIS.get((uni_name, country))
        targets = split if split else [uni_name]

        for target_name in targets:
            coord = CAMPUS_COORDS.get((target_name, country))
            flag = FLAGS.get(country, "🏳")

            prog_list = []
            for r in programs:
                name = r['Course Name'].strip()
                domain = r['Domain'].strip()
                level = r['Credential Level'].strip()
                fee = parse_fee(r['Fee USD'])
                req = r['Minimum Requirements'].strip()
                deadline = r['Deadline'].strip()
                dur = str(r['Course Duration']).strip()
                app_fee = parse_fee(r['Application Fee']) if r['Application Fee'].strip() not in ('', '$-', '0.00  $') else 0
                notes = r['Notes'].strip()

                prog_list.append({
                    "name": name, "domain": domain, "level": level,
                    "feeUSD": fee, "requirements": req, "deadline": deadline,
                    "duration": dur, "appFee": app_fee, "notes": notes
                })

            display_name = target_name if split else uni_name
            city = coord["city"] if coord else ""

            entry = {
                "id": make_id(display_name, country),
                "flag": flag,
                "country": country,
                "uni": display_name,
                "city": city,
                "campus": {"lat": coord["lat"], "lng": coord["lng"]} if coord else None,
                "programs": prog_list
            }
            unis.append(entry)

    # Prepend manual entries
    all_unis = MANUAL_UNIS + unis
    live_unis = [u for u in all_unis if u['campus']]

    # data/universities.js — live universities only (globe-ready), loaded by index.html
    js = "// Auto-generated — edit via scripts/generate-universities.py\n"
    js += "// Live universities (campus coords set). Phase 2: replace with Supabase API fetch.\n"
    js += "const UNIVERSITIES = " + json.dumps(live_unis, ensure_ascii=False, separators=(',',':')) + ";\n"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(js)

    # data/all-universities.json — full database for Phase 2 Supabase migration
    json_path = os.path.join(os.path.dirname(out_path), 'all-universities.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_unis, f, ensure_ascii=False, separators=(',',':'))

    print(f"Written {out_path}")
    print(f"Written {json_path}")
    print(f"Live universities (with campus): {len(live_unis)}")
    print(f"Total universities in database: {len(all_unis)}")
    print(f"Total programs: {sum(len(u['programs']) for u in all_unis)}")
    print(f"universities.js size: {os.path.getsize(out_path)//1024} KB")
    print(f"all-universities.json size: {os.path.getsize(json_path)//1024} KB")
    print()
    print("Live universities:")
    for u in live_unis:
        print(f"  [{u['flag']}] {u['uni']} — {u['city']}, {u['country']} ({len(u['programs'])} programs)")

if __name__ == '__main__':
    main()
