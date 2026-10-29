"""Treatment-page interactives for ix_suite.py: each page's own interactive, really driven."""


def run(pg, vp, cdp, rec, go, into_view, ev, active_index, selected_tab, visible_text, t_xfade, t_range, t_xpanels, acc):
    tap = vp == 390

    def press(loc):
        (loc.tap if tap else loc.click)()

    def act(word):
        return ("tap " if tap else "click ") + word

    def tabs_test(path, name, box, k, expect):
        into_view(pg, box)
        press(pg.locator(f"{box} [role=tab]").nth(k)); pg.wait_for_timeout(500)
        on = selected_tab(pg, box)
        panel = ev(pg, "(b) => { const t = document.querySelector(b + ' [role=tab][aria-selected=true]'); const p = document.getElementById(t.getAttribute('aria-controls')); return !p.hidden && p.offsetHeight > 0 }", box)
        rec(path, name, vp, act(expect), on and expect in on and panel, on)
        if not tap:
            pg.locator(f"{box} [role=tab]").nth(k).focus(); pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(300)
            rec(path, name, vp, "keyboard ArrowRight", selected_tab(pg, box) != on, selected_tab(pg, box))

    def page(path, fn):
        go(pg, path)
        try:
            fn(path)
        except Exception as e:
            rec(path, "interactive", vp, "runs", False, repr(e)[:120])
        acc(pg, path, vp)

    # Dental implants: numbered markers on the implant model
    def implants(path):
        tabs_test(path, "Implant layer explorer", ".hotspots", 2, "3")
        txt = visible_text(pg, ".hotspots__panel")
        rec(path, "Implant layer explorer", vp, "panel names the layer", txt and ("Implant" in txt or "Bone" in txt or "Abutment" in txt), txt)
    page("dental-implants/", implants)

    # Full mouth: stepper with Next / Previous and a progress line
    def phases(path):
        into_view(pg, "[data-stepper]")
        press(pg.locator("[data-stepper] [data-step='1']")); pg.wait_for_timeout(400)
        press(pg.locator("[data-stepper] [data-step='1']")); pg.wait_for_timeout(400)
        at = ev(pg, "() => getComputedStyle(document.querySelector('[data-stepper]')).getPropertyValue('--at').trim()")
        on = selected_tab(pg, "[data-stepper]")
        rec(path, "Phase stepper", vp, act("Next twice"), at == "3" and "Trial" in (on or ""), f"step {at}: {on}")
        press(pg.locator("[data-stepper] [data-step='-1']")); pg.wait_for_timeout(400)
        rec(path, "Phase stepper", vp, act("Previous"), ev(pg, "() => getComputedStyle(document.querySelector('[data-stepper]')).getPropertyValue('--at').trim()") == "2")
        txt = ev(pg, "() => document.querySelector('[data-stepper]').textContent")
        rec(path, "Phase stepper", vp, "no placeholder text", "confirmed" not in txt.lower(), "")
    page("full-mouth-rehabilitation/", phases)

    page("maxillofacial-prosthetics/", lambda path: tabs_test(path, "Who we help selector", ".itabs--side", 2, "injury"))

    def guides(path):
        into_view(pg, "[data-guides]")
        press(pg.locator("[data-guides-toggle]")); pg.wait_for_timeout(600)
        on = ev(pg, "() => [document.querySelector('[data-guides]').classList.contains('is-on'), getComputedStyle(document.querySelector('.guides__lines')).opacity]")
        rec(path, "Design guides overlay", vp, act("Show design guides"), on[0] and float(on[1]) > .5, on)
        press(pg.locator("[data-guides-toggle]")); pg.wait_for_timeout(500)
        rec(path, "Design guides overlay", vp, act("Hide design guides"), not ev(pg, "() => document.querySelector('[data-guides]').classList.contains('is-on')"))
    page("smile-design/", guides)

    page("cosmetic-dentistry/", lambda path: tabs_test(path, "Which fix for which concern", ".matrix", 2, "Gaps"))

    def aligners(path):
        box = "[data-stages]"
        into_view(pg, box)
        inp = pg.locator(f"{box} input[type=range]")
        if tap:
            bb = inp.bounding_box(); pg.touchscreen.tap(bb["x"] + bb["width"] * .7, bb["y"] + bb["height"] / 2)
        else:
            inp.focus(); pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight")
        pg.wait_for_timeout(600)
        v = ev(pg, "(b) => document.querySelector(b + ' input').value", box)
        txt = visible_text(pg, ".stages__text")
        img = active_index(pg, ".stages__img")
        rec(path, "Aligner stage scrubber", vp, "tap stage 3" if tap else "keyboard to stage 3", v == "3" and img == 2 and txt.startswith("Wearing"), f"stage {v}: {txt}")
        tabs_test(path, "Aligners or braces toggle", ".itabs--vs", 1, "Braces")
    page("invisalign/", aligners)

    page("orthodontics/", lambda path: t_xpanels(pg, path, vp, ".xpanels--ix", "Age panels (child/teen/adult)"))

    def timeline(path):
        box = ".drag--timeline"
        into_view(pg, box)
        b0 = ev(pg, "(b) => document.querySelector(b + ' .drag__track').scrollLeft", box)
        press(pg.locator(f"{box} .drag__btn--next")); pg.wait_for_timeout(900)
        b1 = ev(pg, "(b) => document.querySelector(b + ' .drag__track').scrollLeft", box)
        rec(path, "Check-up timeline", vp, act("next arrow"), b1 > b0, f"{b0:.0f} -> {b1:.0f}")
        into_view(pg, box + " .drag__track")
        if not tap:
            bb = pg.locator(f"{box} .drag__track").bounding_box()
            pg.mouse.move(bb["x"] + bb["width"] * .7, bb["y"] + 120); pg.mouse.down()
            pg.mouse.move(bb["x"] + bb["width"] * .3, bb["y"] + 120, steps=10); pg.mouse.up(); pg.wait_for_timeout(900)
            b2 = ev(pg, "(b) => document.querySelector(b + ' .drag__track').scrollLeft", box)
            rec(path, "Check-up timeline", vp, "mouse drag", b2 > b1, f"{b1:.0f} -> {b2:.0f}")
        else:
            bb = pg.locator(f"{box} .drag__track").bounding_box()
            def touch(kind, pts):
                cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": a, "y": c} for a, c in pts]})
            touch("touchStart", [(bb["x"] + bb["width"] * .8, bb["y"] + 100)])
            for k in range(1, 12):
                touch("touchMove", [(bb["x"] + bb["width"] * (.8 - .05 * k), bb["y"] + 100)]); pg.wait_for_timeout(16)
            touch("touchEnd", []); pg.wait_for_timeout(900)
            b2 = ev(pg, "(b) => document.querySelector(b + ' .drag__track').scrollLeft", box)
            rec(path, "Check-up timeline", vp, "swipe", b2 > b1, f"{b1:.0f} -> {b2:.0f}")
        rec(path, "Check-up timeline", vp, "#gum-care anchor exists", ev(pg, "() => !!document.getElementById('gum-care')"))
    page("general-dentistry/", timeline)

    page("root-canal-treatment/", lambda path: t_xfade(pg, path, vp, "Root canal steps", "[data-xfade]", ["01Infected pulp", "02Cleaned", "03Sealed and checked"]))

    def crowns(path):
        tabs_test(path, "Crown material tabs", ".itabs--split", 1, "Zirconia")
        box = "[data-decider]"
        into_view(pg, box)
        press(pg.locator(f"{box} label", has_text="No, it is missing")); pg.wait_for_timeout(400)
        press(pg.locator(f"{box} [data-show-if='there:no'] label").first); pg.wait_for_timeout(400)
        out = visible_text(pg, "[data-decider] [data-when]")
        rec(path, "Crown, bridge or implant? decider", vp, act("missing, healthy sides"), out and out.startswith("Often an implant"), out)
    page("crowns-bridges/", crowns)

    page("kids-dentistry/", lambda path: tabs_test(path, "Kids age guide", ".itabs--split", 2, "Ages"))
