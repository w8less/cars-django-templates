import re

from apps.main.models import Car, Mark, Model


def find_same_car(data: dict, site: str):
    car = Car.objects.filter(**{
        'model_id': data['model_id'],
        'fuel': data['fuel'],
        'drive': data['drive'],
        'gearbox': data['gearbox'],
        'year': data['year'],
        'mileage__gte': data['mileage'] - 1000,
        'mileage__lte': data['mileage'] + 1000,
        'price__gte': data['price'] - 1000,
        'price__lte': data['price'] + 1000,
        'engine': data['engine'],
        'seller': data['seller'],
        'body': data['body'],
        'location': data['location'],
        'dtp': data['dtp'],
        'cleared': data['cleared'],
        'carlink__site': site})
    return car.first() if car else None


def get_model_id(mark, model):
    old_mark = mark
    old_model = model
    if mark and model:
        mark = re.sub(r"greatwall", "great-wall", mark)
        mark = re.sub(r"ssang-yong", "ssangyong", mark)
        mark = re.sub(r"(moscvich|moskvich-azlk)", "moskvich", mark)
        mark = re.sub(r"mercedes-benz", "mercedes", mark)
        mark = re.sub(r"alfaromeo", "alfa-romeo", mark)
        mark = re.sub(r"landrover", "land-rover", mark)

        mark_obj = Mark.objects.filter(eng=mark).first()
        mark_id = mark_obj.id if mark_obj else None

        if mark_id:
            model = re.sub(r"(-gruz-pass|-gruz|-pass|-1)", "", model)

            if mark_id == 4:
                model = re.sub(r"-4", "", model)
            elif mark_id == 11:
                model = re.sub(r"rs-3", "rs3", model)
                model = re.sub(r"rs-4", "rs4", model)
                model = re.sub(r"rs-5", "rs5", model)
                model = re.sub(r"rs-6", "rs6", model)
                model = re.sub(r"rs-7", "rs7", model)
                model = re.sub(r"(rs-6|audi-rs-6-avant)", "rs6", model)
                model = re.sub(r"(audi-|-7|-2|-3|-4)", "", model)
            elif mark_id == 18:
                model = re.sub(r"(-gt|-flying-spur)", "", model)
            elif mark_id == 22:
                model = re.sub(r"(-2|-m)", "", model)
                model = re.sub(r"seriya", "series", model)
                model = re.sub(r"([0-9])[0-9]{2}", r"\1-series", model)
            elif mark_id == 34:
                model = re.sub(r"tigo", "tiggo", model)
                model = re.sub(r"(-2|-3|-4|-5|-6|-7)", "", model)
                model = re.sub(r"sweet-qq", "qq", model)
                model = re.sub(r"^qq.+?$", "qq", model)
                model = re.sub(r"^kimo.+?$", "kimo", model)
                model = re.sub(r"a21", "elara", model)
            elif mark_id == 35:
                model = re.sub(r"lacetti(-variant|-hatchback|-furgon|-pick-up|-sedan)", "lacetti", model)
                model = re.sub(r"lanos(-sens|-hatchback|-furgon|-pick-up|-sedan|-2)", "lanos", model)
                model = re.sub(r"(-ev|-2|-express)", "", model)
            elif mark_id == 36:
                model = re.sub(r"(-3|-2)", "", model)
                model = re.sub(r"300(c|m|s)", "300-\1", model)
            elif mark_id == 37:
                model = re.sub(r"(citroen-|-picasso|-multispace|-spacetourer)", "", model)
                model = re.sub(r"(-mcv|-stepway|-van|-aircross|-vp|-vu)", "", model)
            # elif mark_id == 38:
            #     model = re.sub(r"-1", "", model)
            elif mark_id == 40:
                model = re.sub(r"(-sens|-hatchback|-furgon|-pick-up|-sedan|-2|-3|-sx)", "", model)
            elif mark_id == 51:
                model = re.sub(r"-2", "", model)
            elif mark_id == 59:
                model = re.sub(r"new-500", "500", model)
                model = re.sub(r"500(l|x|-2)", "500", model)
                model = re.sub(r"grandepunto", "grande-punto", model)
                model = re.sub(r"(-2|-abarth|)", "", model)
            elif mark_id == 62:
                model = re.sub(r"(-2|-3)", "", model)
                model = re.sub(r"fiesta-st", "fiesta", model)
                model = re.sub(r"^connect$", "tourneo-connect", model)
                model = re.sub(r"^tourneo$", "tourneo-connect", model)
                model = re.sub(r"^connect-tourneo$", "tourneo-connect", model)
                model = re.sub(r"^connect-transit$", "transit-connect", model)
            elif mark_id == 67:
                model = re.sub(r"emgrandx(\d)", "emgrand-x\1", model)
                model = re.sub(r"emgrand[0-9\-].+?$", "emgrand", model)
                model = re.sub(r"emgrand-?([0-9])$", "emgrand", model)
            elif mark_id == 71:
                model = re.sub(r"^.*?voleex.*?$", "voleex", model)
                model = re.sub(r"^.*?haval.*?$", "haval", model)
            # elif mark_id == 78:
            #     model = re.sub(r"-1", "", model)
            elif mark_id == 85:
                model = re.sub(r"(-starex|-7|-electric|-coupe|-fastback)", "", model)
                model = re.sub(r"^h$", "h1", model)
                model = re.sub(r"h([0-9]{3})", r"h-\1", model)
                model = re.sub(r"^.*?ix55.*?$", "ix55", model)
                model = re.sub(r"santafe", "santa-fe", model)
            elif mark_id == 86:
                model = re.sub(r"(qx|q|m|g)-([0-9]{2})", r"\1\2", model)
                model = re.sub(r"-series", "", model)
            elif mark_id == 95:
                model = re.sub(r"-unlimited", "", model)
                model = re.sub(r"^grandcherokee$", "grand-cherokee", model)
            elif mark_id == 102:
                model = re.sub(r"^.*?rio.*?$", "rio", model)
                model = re.sub(r"^.*?cerato.*?$", "cerato", model)
                model = re.sub(r"^.*?ceed.*?$", "ceed", model)
                model = re.sub(r"(-ev|-ii)", "", model)
            elif mark_id == 109:
                model = re.sub(r"^rangeroversport", "range-rover-sport", model)
                model = re.sub(r"^rangerover", "range-rover", model)
                model = re.sub(r"^evoque", "range-rover-evoque", model)
                model = re.sub(r"(-velar|-supercharged|-vogue)", "", model)
            elif mark_id == 112:
                model = re.sub(r"(-seriya|-450-h|-450d|-460|-470|-200t|-200h|-300h|-350|-250h|-570)", "", model)
            elif mark_id == 122:
                model = re.sub(r"(-3|-4|-5)", "", model)
                model = re.sub(r"xedos6", "xedos-6", model)
                model = re.sub(r"xedos9", "xedos-9", model)
                model = re.sub(r"e-2000-2200-bus", "e-series", model)
                model = re.sub(r"cx-6", "cx-5", model)
                model = re.sub(r"cx([0-9])", r"cx-\1", model)
            elif mark_id == 125:
                model = re.sub(r"(-coupe|-roadster-r190|-c-190)", "", model)
                model = re.sub(r"(seriya|klass)", "class", model)
                model = re.sub(r"maybach-s-class-x222", "maybach", model)
                model = re.sub(r"sprinter-\d+$", "sprinter", model)
                model = re.sub(r"(w(124|123)|w114-w115)", "e-class", model)
                model = re.sub(r"class-550", "550", model)
                model = re.sub(r"(aamg-gt-4|amg(-gt|-gt-c-190|-gt-roadster-r190|-c90))", "amg", model)
                model = re.sub(r"^(gl|glk|gls|glc|gle|ml|g|sl|slk|cls|clk|clc|cla|a|b|cl|s|r|v|m|e|c)$", r"\1-class", model)
                model = re.sub(r"^(gl|glk|gls|glc|gle|ml|g|sl|slk|cls|clk|clc|cla|a|b|cl|s|r|v|m|e|c)(-[0-9]{3}|[0-9]{2}|[0-9]{3}|-[0-9]{3}\w+|-klass)$", r"\1-class", model)
                model = re.sub(r"^(gl|glk|gls|glc|gle|ml|g|sl|slk|cls|clk|clc|cla|a|b|cl|s|r|v|m|e|c)\-[0-9]{2}\-amg$", r"\1-class", model)
                model = re.sub(r"^(gls|s)-[0-9]{2}", r"\1-class", model)
            elif mark_id == 128:
                model = re.sub(r"(-2|-cross)", "", model)
            elif mark_id == 130:
                model = re.sub(r"cooper(-hatch|-countryman|-clubman)", "cooper", model)
                model = re.sub(r"cooper-s(-hatch|-countryman|-clubman)", "cooper-s", model)
                model = re.sub(r"cooper-d(-hatch|-countryman|-clubman)", "cooper-d", model)
            elif mark_id == 131:
                model = re.sub(r"mitsubishi-l200", "l-200", model)
                model = re.sub(r"lanser", "lancer", model)
                model = re.sub(r"eclipse-cross", "eclipse", model)
                model = re.sub(r"spacestar", "space-star", model)
                model = re.sub(r"spacewagon", "space-wagon", model)
                model = re.sub(r"^lancer.+?$", "lancer", model)
                model = re.sub(r"pajerosport", "pajero-sport", model)
                model = re.sub(r"l([0-9]00)", r"l-\1", model)
            elif mark_id == 135:
                model = re.sub(r"(-gr|e-|-ii|-bluebird|-sunny|-nismo-rs)", "", model)
                model = re.sub(r"almera-classic", "almera", model)
                model = re.sub(r"skyline-gt-r", "skyline", model)
                model = re.sub(r"(nv200|nv300|nv400)", "nv", model)
                model = re.sub(r"350-z", "350z", model)
                model = re.sub(r"^maxima.+?$", "maxima", model)
                model = re.sub(r"^micra.+?$", "micra", model)
                model = re.sub(r"^qashqai.+?$", "qashqai", model)
            elif mark_id == 140:
                model = re.sub(r"record", "rekord", model)
                model = re.sub(r"(-3|-sports-tourer|-2|-x|-g|-4)", "", model)
            elif mark_id == 146:
                model = re.sub(r"(-tepee|-sedan|-gti|-2|-sw|-cc|-ss|-hatchback-5d|-hatchback-3d)", "", model)
                model = re.sub(r"j5", "g-5", model)
            elif mark_id == 151:
                model = re.sub(r"^cayenne.+?$", "cayenne", model)
            elif mark_id == 156:
                model = re.sub(r"-", "", model)
            elif mark_id == 157:
                model = re.sub(r"(-passenger|-2|-scenic|-z-e)", "", model)
                model = re.sub(r"logan-mcv", "logan", model)
                # model = re.sub(r"^(kangoo|scenic|clio|symbol).*?$", "\1", model)
            elif mark_id == 178:
                model = re.sub(r"(-new|-combi)", "", model)
                model = re.sub(r"^octavia.+?$", "octavia", model)
                model = re.sub(r"^fabia.+?$", "fabia", model)
            elif mark_id == 187:
                model = re.sub(r"(-outback|-wagon|-sti-sedan)", "", model)
                model = re.sub(r"^impreza.+?$", "impreza", model)
            elif mark_id == 189:
                model = re.sub(r"-1", "", model)
                model = re.sub(r"grandvitara", "grand-vitara", model)
            elif mark_id == 201:
                model = re.sub(r"(rav4|rav-4-ev)", "rav-4", model)
                model = re.sub(r"(-hybrid|-plus|-e|-ev|-76|-80|-90)", "", model)
                model = re.sub(r"^.*?land-cruiser-prado.*?$", "land-cruiser-prado", model)
                model = re.sub(r"landcruiser", "land-cruiser", model)
                model = re.sub(r"hilux-pick-up", "hilux", model)
                model = re.sub(r"corolla-fx", "corolla", model)
                model = re.sub(r"^prado$", "land-cruiser-prado", model)
                model = re.sub(r"land-cruiser-[0-9]{3}", "land-cruiser", model)
            elif mark_id == 210:
                model = re.sub(r"(-sedan|-variant|-hatchback|-kombi-maxi|-kasten-maxi|-kasten|-maxi|-kombi|-allspace|t4-|t5-|t6-|t6-1-|-alltrack|e-)", "", model)
                model = re.sub(r"t\d+\-transporter", "transporter", model)
                model = re.sub(r"^passat\-b\d+$", "passat", model)
                model = re.sub(r"camper", "transporter", model)
                model = re.sub(r"^golf.+?$", "golf", model)
                model = re.sub(r"t[0-9]", "transporter", model)
                model = re.sub(r"^cc$", "passat-cc", model)
                model = re.sub(r"lt-2", "lt", model)
            elif mark_id == 211:
                model = re.sub(r"(-kombi|-k|volvo-|-cross-country|-2)", "", model)
                model = re.sub(r"s-60-cc", "s60", model)
            elif mark_id == 228:
                model = re.sub(r"-1", "", model)
                # model = re.sub(r"^.*?(kalina|priora).*?$", "\1", model)
                # model = re.sub(r"^21(0[1-8]|[1-9][0-9]|099|093|09).*?$", "21\1", model)
                model = re.sub(r"1111-oka", "oka", model)
            elif mark_id == 230:
                model = re.sub(r"(-zim|lada-|-chayka)", "", model)
                model = re.sub(r"^.*?sobol.*?$", "sobol", model)
                model = re.sub(r"^.*?pobeda.*?$", "20", model)
                model = re.sub(r"^.*?gazel.*?$", "gazel", model)
                model = re.sub(r"24-10-volga", "24", model)
                model = re.sub(r"2790", "gazel", model)
                model = re.sub(r"^(21|23|24|24[0-9]{2}|3110[0-9]?|3109|(31029|24|3110|31105|21)-volga)$", "volga", model)
            elif mark_id == 236:
                model = re.sub(r"^(1102|1140).*?$", "tavriya", model)
                model = re.sub(r"^(1105|1125).*?$", "dana", model)
                model = re.sub(r"^1103.*?$", "slavuta", model)
                model = re.sub(r"(tavria-pickup|tavria)", "tavriya", model)
                model = re.sub(r"lanos(-sens|-hatchback|-furgon|-pick-up|-pickup|-sedan|-cargo)", "lanos", model)
                model = re.sub(r"968m", "968", model)
                model = re.sub(r"(-cargo|-nova|1122-)", "", model)
            elif mark_id == 240:
                pass
            elif mark_id == 242 and model == '2125':
                mark_id = 240
            elif mark_id == 242:
                model = re.sub(r"-2", "", model)
                model = re.sub(r"^.*?2141.*?$", "2141", model)
                model = re.sub(r"^.*?2135.*?$", "2335", model)
            elif mark_id == 254:
                model = re.sub(r"^.*?hunter.*?$", "hunter", model)
                model = re.sub(r"^.*?patriot.*?$", "patriot", model)

            model_obj = Model.objects.filter(eng=model, mark_id=mark_id).first()
            model_id = model_obj.id if model_obj else None

            if model_id:
                return model_id

    print('Not save {} {}'.format(mark, model))

    with open('not_saved.json', 'a+', encoding='utf8') as f:
        import json
        json.dump({'mark': mark, 'model': model, 'old_mark': old_mark, 'old_model': old_model}, f, ensure_ascii=False)
        f.write(',\n')
    return None
