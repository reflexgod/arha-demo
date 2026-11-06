"""The site chrome, written into index.html by tools/pages.py and copied from there to every page:
the header (logo, navigation, the clinic's number and its call panel), the phone menu and the footer.

Built on apaaesthetic.com's system (notes/apa-study.md, notes/V4-PROBLEMS-FIRST.md): WHAT WE TREAT · WHO WE ARE
· OUR WORK · BOOK A CONSULTATION centred, CALL NOW and a menu button on the right; a full-screen menu with
+ groups at every width; a calm dark footer. Contact details are placeholders, rewritten from SITE.
"""
from home import ARROW
import problems
import treatments

# WhatsApp: one prefilled message everywhere. The number is SITE["whatsapp"] in tools/pages.py (TODO-CONFIRM).
WA_TEXT = "Hi, I'd like to request an appointment at Arha Dental Care."
WA = "https://wa.me/910000000000?text=Hi%2C%20I%27d%20like%20to%20request%20an%20appointment%20at%20Arha%20Dental%20Care."
WA_ICON = ('<svg class="icon-wa" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3Z" '
           'fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M9 8.2c.2-.4.5-.4.7-.4h.5c.2 0 .4 0 .5.4l.7 1.6c.1.2 0 .4-.1.6l-.5.6c-.1.1-.1.3 0 .5.6 1 1.4 1.8 2.4 2.4.2.1.4.1.5 0l.6-.6c.2-.2.4-.2.6-.1l1.6.8c.3.1.3.3.3.5v.5c0 .3-.1.6-.5.8-.6.4-1.4.6-2.3.3-1.6-.5-3.6-2.3-4.4-3.8-.6-1.1-.8-2.1-.6-2.8Z" fill="currentColor"/></svg>')

PHONE = ('<svg class="icon-phone" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>')
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&amp;destination=Arha%20Dental%20Care%2C%20Doctor%20House%2C%2014%20Peddar%20Road%2C%20Mumbai%20400026"

WHO = [("founder/", "About the founder"), ("doctors/", "The doctors"), ("the-practice/", "The practice"),
       ("gallery/", "Gallery")]


def _links(items, i):
    # Gallery is listed under Who we are only while Our work has the nav slot (SITE["showOurWork"])
    return "".join((f'\n{i}<!--flag:ourwork--><li><a href="{href}">{name}</a></li><!--/flag:ourwork-->' if href == "gallery/" and items is WHO
                    else f'\n{i}<li><a href="{href}">{name}</a></li>') for href, name in items)


def what_we_fix():
    """WHAT WE TREAT: the ten problems and every treatment, plus Technology, Kids' dentistry and Dental tourism."""
    probs = [(f"problems/{s}/", problems.PROBLEMS[s]["menu"]) for s in problems.ORDER]
    treats = [(f'{t["slug"]}/', t["name"]) for g in treatments.GROUPS for t in g["items"] if t["slug"] != "kids-dentistry"]
    return probs, treats


def header():
    """v9: one slim row (72 px laptops, 60 px phones). Logo | What we treat, Who we are, Gallery, Contact | the live
    open status, WhatsApp and a solid Book button. Over the homepage video it is transparent with light text; after
    80 px of scroll it turns cream with a hairline (site.js 1). Phones: logo | WhatsApp | menu."""
    probs, treats = what_we_fix()
    also = [("technology/", "Technology &amp; innovation"), ("kids-dentistry/", "Kids’ dentistry"), ("dental-tourism/", "Dental tourism")]
    return f"""  <!-- ===================================================================== HEADER -->
  <header class="site-header" data-header>
    <div class="site-header__inner">
      <a class="brand" href="./" aria-label="Arha Dental Care, home"><img class="brand__dark" src="assets/logo/logo-lockup-dark.svg" alt="" width="150" height="38"><img class="brand__light" src="assets/logo/logo-lockup-light.svg" alt="" width="150" height="38"></a>

      <nav class="nav" aria-label="Main">
        <ul class="nav__list">
          <li class="nav__item nav__item--mega" data-dropdown>
            <button class="nav__trigger" type="button" aria-expanded="false" aria-controls="dd-fix">What we treat</button>
            <div class="dropdown dropdown--mega" id="dd-fix">
              <div class="mega mega--fix">
                <div class="mega__group">
                  <p class="mega__title"><a href="problems/">Problems</a></p>
                  <ul class="mega__cols">{_links(probs, "                    ")}
                  </ul>
                </div>
                <div class="mega__group">
                  <p class="mega__title"><a href="treatments/">Treatments</a></p>
                  <ul class="mega__cols">{_links(treats + also, "                    ")}
                  </ul>
                </div>
                <div class="mega__urgent-box">
                  <p class="mega__urgent-title">Dental emergency?</p>
                  <p><!--if:phone--><a class="mega__call" href="tel:+910000000000" data-call="mega" data-label="phone" aria-label="Call Arha Dental Care now, +91 00000 00000">{PHONE}<span>Call now</span></a><!--endif--><a class="mega__urgent" href="emergency/">Get help now</a></p>
                </div>
              </div>
            </div>
          </li>
          <li class="nav__item" data-dropdown>
            <button class="nav__trigger" type="button" aria-expanded="false" aria-controls="dd-who">Who we are</button>
            <ul class="dropdown" id="dd-who">{_links(WHO, "              ")}
            </ul>
          </li>
          <li class="nav__item"><!--flag:ourwork--><a class="nav__link" href="our-work/">Our work</a><!--/flag:ourwork--><!--flag:no-ourwork--><a class="nav__link" href="gallery/">Gallery</a><!--/flag:no-ourwork--></li>
          <li class="nav__item"><a class="nav__link" href="the-practice/#visit">Contact</a></li>
        </ul>
      </nav>

      <div class="header-actions">
        <p class="header-status" data-open-status></p>
        <!--if:whatsapp--><a class="header-wa" href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp Arha Dental Care">{WA_ICON}</a><!--endif-->
        <a class="btn btn--primary header-book" href="book/"><span>Book an appointment</span>{ARROW}</a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="side-menu" aria-label="Open menu">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </header>
"""


def side_menu():
    """apa's full-screen menu (every width): large items, a + opens a group in place (site.js 3).
    Lists every tab Neha ma'am asked for, the ten problems and every treatment."""
    probs, treats = what_we_fix()

    def group(key, title, inner):
        return f"""
            <li class="fmenu__group">
              <button class="fmenu__toggle" type="button" aria-expanded="false" aria-controls="fm-{key}">{title}<span class="plus" aria-hidden="true"></span></button>
              <div class="fmenu__sub" id="fm-{key}" hidden>{inner}
              </div>
            </li>"""
    fix = (f'\n                <p class="fmenu__label"><a href="problems/">Problems we treat</a></p><ul>{_links(probs, "                  ")}\n                </ul>'
           f'\n                <p class="fmenu__label"><a href="treatments/">Treatments</a></p><ul>{_links(treats, "                  ")}\n                </ul>')
    who = f'\n                <ul>{_links(WHO, "                  ")}\n                </ul>'
    return f"""
  <!-- ===================================================================== MENU (full screen, every width) -->
  <div class="side-menu" id="side-menu" role="dialog" aria-modal="true" aria-label="Menu" inert>
    <div class="side-menu__panel">
      <div class="side-menu__top">
        <img src="assets/logo/logo-lockup-dark.svg" alt="Arha Dental Care" width="140" height="36">
        <button class="side-menu__close" type="button" data-close aria-label="Close menu"></button>
      </div>
      <nav class="fmenu" aria-label="Menu" data-fmenu>
        <ul class="fmenu__list">{group("fix", "What we treat", fix)}{group("who", "Who we are", who)}
            <li><!--flag:ourwork--><a class="fmenu__link" href="our-work/">Our work</a><!--/flag:ourwork--><!--flag:no-ourwork--><a class="fmenu__link" href="gallery/">Gallery</a><!--/flag:no-ourwork--></li>
            <li><a class="fmenu__link" href="technology/">Technology &amp; innovation</a></li>
            <li><a class="fmenu__link" href="kids-dentistry/">Kids’ dentistry</a></li>
            <li><a class="fmenu__link" href="dental-tourism/">Dental tourism</a></li>
        </ul>
        <div class="fmenu__actions">
          <a class="btn btn--primary" href="book/"><span>Book an appointment</span>{ARROW}</a>
          <!--if:phone--><a class="btn" href="tel:+910000000000" data-call="menu"><span>Call</span>{ARROW}</a><!--endif-->
          <!--if:whatsapp--><a class="btn" href="{WA}" target="_blank" rel="noopener"><span>WhatsApp</span>{ARROW}</a><!--endif-->
        </div>
        <ul class="fmenu__small">
          <li><a href="the-practice/#visit">Visit us</a></li>
          <li><a href="emergency/">Dental emergencies</a></li>
        </ul>
      </nav>
      <div class="side-menu__foot">
        <a href="tel:+910000000000" data-call="menu" data-show="phone">+91 00000 00000</a>
        <p class="open-status" data-open-status></p>
        <p><a href="{WA}" target="_blank" rel="noopener">WhatsApp</a> · <a href="mailto:hello@example.com">Email</a></p>
        <p>107, Doctor House, 14 Peddar Road, Mumbai 400026</p>
      </div>
    </div>
  </div>
"""


def footer():
    explore = [("problems/", "What we treat"), ("treatments/", "Treatments"), ("technology/", "Technology &amp; innovation"),
               ("founder/", "About the founder"), ("doctors/", "The doctors"), ("the-practice/", "The practice"),
               ("gallery/", "Gallery"), ("kids-dentistry/", "Kids’ dentistry"), ("dental-tourism/", "Dental tourism"), ("book/", "Book an appointment")]
    explore.insert(3, ("our-work/", "Our work"))
    links = "".join((f'\n            <!--flag:ourwork--><li><a href="{h}">{n}</a></li><!--/flag:ourwork-->' if h == "our-work/"
                     else f'\n            <li><a href="{h}">{n}</a></li>') for h, n in explore)
    return f"""  <!-- ===================================================================== FOOTER -->
  <footer class="site-footer" data-footer>
    <div class="container">
      <p class="footer__tagline">Dr. Nikhil V. Jain’s clinic on Peddar Road</p>
      <img class="footer__logo" src="assets/logo/logo-lockup-light.svg" alt="Arha Dental Care" width="220" height="56" loading="lazy">
      <p class="footer__book"><a class="btn btn--light" href="book/"><span>Book an appointment</span>{ARROW}</a></p>
      <div class="footer__cols">
        <div>
          <h2>Visit</h2>
          <address>
            107, Doctor House<br>
            14 Peddar Road (Dr Gopalrao Deshmukh Marg)<br>
            Opp. Jaslok Hospital<br>
            Mumbai 400026
          </address>
          <p class="footer__directions"><a href="{DIRECTIONS}" target="_blank" rel="noopener">Get directions</a></p>
        </div>
        <div>
          <h2>Hours</h2>
          <p><span data-show="hours-days">Monday to Saturday</span><br><span data-show="hours-time">9:30 AM to 6:30 PM</span><br><span data-show="hours-closed">Sunday closed</span></p>
          <p class="open-status footer__status" data-open-status></p>
        </div>
        <div>
          <h2>Contact</h2>
          <ul>
            <li><a href="tel:+910000000000" data-call="footer" data-show="phone">+91 00000 00000</a></li>
            <li><a href="{WA}" target="_blank" rel="noopener">WhatsApp</a></li>
            <li><a href="mailto:hello@example.com" data-show="email">hello@example.com</a></li>
            <li><a href="book/">Book an appointment</a></li>
            <li><a href="emergency/">Dental emergencies: <span data-show="emergency">+91 00000 00000</span></a></li>
          </ul>
        </div>
        <nav aria-labelledby="footer-explore">
          <h2 id="footer-explore">Explore</h2>
          <ul>{links}
          </ul>
        </nav>
      </div>
      <div class="footer__bottom">
        <p>© 2026 Arha Dental Care</p>
        <ul>
          <!-- Privacy: added with the privacy policy text (notes/TO-CONFIRM.md); no link to an empty page -->
          <li>Demo prepared by Viraaj</li>
        </ul>
      </div>
    </div>
  </footer>
"""


def call_bar():
    """The action bar on phones, on every page from the first paint: two actions, one tap each. Call now (with
    today's status, site.js 12) once the clinic's number is real; until then Emergencies, so a patient in pain still
    has a way in. Book is always there. It waits while the page's hero has its own booking button, and steps aside
    while another call link is on screen (site.js 7), so a number or call button shows at most once."""
    return f"""  <!-- ===================================================================== ACTION BAR (phones)
       Generated by tools/chrome.py. The Call slot appears only with a real reception number (tools/pages.py). -->
  <!--if:whatsapp--><a class="wa-float" href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp Arha Dental Care">{WA_ICON}</a><!--endif-->
  <nav class="call-bar call-bar--two" aria-label="Call or book">
    <!--if:phone--><a class="call-bar__slot" href="tel:+910000000000" data-call="call_bar"><span class="call-bar__label" data-call-label data-open="Call now" data-closed="Call">Call now</span><span class="visually-hidden">: call Arha Dental Care, <span data-show="phone">+91 00000 00000</span>.</span><span class="call-bar__status" data-call-status data-show="hours-short">Mon–Sat 9:30 AM–6:30 PM</span></a><!--endif-->
    <!--if:no-phone--><a class="call-bar__slot" href="emergency/"><span class="call-bar__label">Emergency</span><span class="call-bar__status">Help and first aid</span></a><!--endif-->
    <a class="call-bar__slot" href="book/"><span class="call-bar__label">Book appointment</span><span class="call-bar__status"><!--if:phone-->In person or online<!--endif--><!--if:no-phone--><span data-call-status data-show="hours-short">Mon–Sat 9:30 AM–6:30 PM</span><!--endif--></span></a>
  </nav>
"""
