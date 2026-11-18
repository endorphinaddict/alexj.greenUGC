/* Hook Lab — data + generation engine. No dependencies. */
(function (root) {
  "use strict";

  /* ---------- Product category presets ----------
     pains / benefits are noun phrases so they slot into any template.
     Click-to-add chips in the UI pull from these. */
  const CATEGORIES = {
    skincare: {
      label: "Skincare / beauty", noun: "skincare product",
      audiences: ["women over 30", "people with sensitive skin", "acne-prone girls", "people with dry skin"],
      pains: ["breakouts", "dull skin", "dry, flaky skin", "dark circles", "a 10-step routine that does nothing"],
      benefits: ["clear skin", "glowing skin", "a smoother texture", "skin that actually feels hydrated"],
      visuals: ["Close-up of bare skin in natural window light", "Texture swatch on the back of your hand", "Product pump or dropper in slow motion", "Mirror shot applying it"]
    },
    supplements: {
      label: "Supplements / wellness", noun: "supplement",
      audiences: ["busy moms", "people who crash at 3pm", "gym girls", "people over 40"],
      pains: ["afternoon crashes", "brain fog", "bloating", "bad sleep", "low energy"],
      benefits: ["steady energy", "a calmer gut", "deeper sleep", "a clearer head"],
      visuals: ["Tipping the capsules or scoop into your palm", "Stirring a drink in a real kitchen", "Counting out your morning stack", "Yawning at your desk, then a cut to energized"]
    },
    kitchen: {
      label: "Kitchen / home goods", noun: "kitchen gadget",
      audiences: ["people who hate doing dishes", "busy parents", "meal preppers", "small-apartment cooks"],
      pains: ["a cluttered counter", "soggy leftovers", "dinner taking an hour", "piles of dishes"],
      benefits: ["dinner in ten minutes", "a spotless counter", "food that stays fresh", "half the cleanup"],
      visuals: ["Messy counter before, clean after", "Product in use mid-recipe", "Sound-on close-up (sizzle, click, pour)", "Side-by-side with the old way"]
    },
    fitness: {
      label: "Fitness / activewear", noun: "workout piece",
      audiences: ["gym beginners", "girls who lift", "runners", "people working out at home"],
      pains: ["leggings that roll down", "boring workouts", "sore recovery days", "no time for the gym"],
      benefits: ["a workout that actually sticks", "faster recovery", "gear that stays put", "a full session in 20 minutes"],
      visuals: ["Mid-rep close-up", "Squat test to prove the fit", "Unboxing on the gym floor", "Before/after of sore muscles stretching"]
    },
    pets: {
      label: "Pet products", noun: "pet product",
      audiences: ["dog moms", "cat owners", "puppy owners", "people with shedding pets"],
      pains: ["fur on everything", "a bored pup", "chewed-up furniture", "a stinky dog bed"],
      benefits: ["a fur-free couch", "a happy, tired dog", "a pet that finally settles", "a home that smells clean"],
      visuals: ["Your pet's reaction in real time", "Lint roller test on the couch", "Pet using it with no coaxing", "Wide shot of the chaos before"]
    },
    tech: {
      label: "Tech / gadgets", noun: "gadget",
      audiences: ["remote workers", "people with a messy desk setup", "iPhone users", "frequent travelers"],
      pains: ["a dead phone at 2pm", "tangled cables", "a desk that looks chaotic", "slow, unreliable gear"],
      benefits: ["a clean desk setup", "all-day battery", "one cable for everything", "a setup that just works"],
      visuals: ["Desk before vs after", "Screen recording of it working", "Plug it in and show the result", "Hand-held unboxing, no cuts"]
    },
    fashion: {
      label: "Fashion / accessories", noun: "wardrobe staple",
      audiences: ["girls who hate shopping", "petite girls", "people who overpack", "capsule-wardrobe builders"],
      pains: ["clothes that never fit right", "nothing to wear", "pieces that fall apart after one wash", "a closet full of 'meh'"],
      benefits: ["an outfit in 30 seconds", "pieces that last", "a perfect fit", "a closet I actually wear"],
      visuals: ["Try-on with a quick transition cut", "Fabric stretch and hand-feel close-up", "Outfit-of-the-day in a mirror", "Closet pan before the reveal"]
    },
    baby: {
      label: "Baby / parenting", noun: "parenting essential",
      audiences: ["new moms", "sleep-deprived parents", "first-time dads", "moms of toddlers"],
      pains: ["bedtime battles", "nonstop mess", "a fussy baby", "no time for yourself"],
      benefits: ["an easier bedtime", "five minutes to yourself", "a calmer house", "one less thing to worry about"],
      visuals: ["Real-life chaos then calm", "Product in use at the exact hard moment", "One-handed demo (parent holding baby)", "Hand reaching into frame"]
    },
    food: {
      label: "Food / drink", noun: "snack",
      audiences: ["people trying to eat healthier", "sweet-tooth girls", "coffee addicts", "busy students"],
      pains: ["snacks that taste like cardboard", "a 3pm sugar crash", "boring healthy food", "overpriced coffee"],
      benefits: ["a snack I actually crave", "no sugar crash", "a better-than-cafe latte", "healthy food that tastes good"],
      visuals: ["First bite reaction", "Pour/stir/crunch ASMR close-up", "Prep it in real time", "Taste-test with an honest face"]
    },
    home: {
      label: "Home / cleaning / decor", noun: "home product",
      audiences: ["renters", "people with small apartments", "people who hate cleaning", "new homeowners"],
      pains: ["a bathroom that never looks clean", "stubborn stains", "a room that feels cold", "storage chaos"],
      benefits: ["a space that feels expensive", "a one-swipe clean", "a cozy room for cheap", "everything in its place"],
      visuals: ["Before/after of one surface", "Satisfying wipe or spray in extreme close-up", "Quick room-reveal pan", "Time-lapse of the setup"]
    },
    general: {
      label: "Other / generic", noun: "product",
      audiences: ["people who've tried everything", "people who are tired of overpaying", "busy people"],
      pains: ["products that don't work", "doing everything the hard way", "the same problem every week"],
      benefits: ["a simple fix", "better results with less effort", "something that finally works"],
      visuals: ["Product in hand, direct to camera", "Real-life problem moment, then the product", "Side-by-side before/after", "Unboxing with a genuine reaction"]
    }
  };

  /* ---------- Hook types ----------
     `emotion`: what the viewer should feel in the first 2 seconds.
     `visual`: what to show on screen with the line. */
  const HOOK_TYPES = {
    callout:  { label: "Audience callout", emotion: "Recognition",
                visual: "Talk straight to camera, tight framing. Name the audience in on-screen text in the first second." },
    question: { label: "Curiosity question", emotion: "Curiosity",
                visual: "Start mid-motion with a puzzled or knowing face. Hold the product just out of frame, then reveal." },
    confession:{label: "Confession / relief", emotion: "Relief",
                visual: "Casual, low-fi, couch or kitchen. Slight eye-roll or sigh before the line lands." },
    pov:      { label: "POV", emotion: "Relatability",
                visual: "Act the moment out. Show the frustrating situation, then a quick cut to the fix." },
    shock:    { label: "Stop-scroll shock", emotion: "Frustration → urgency",
                visual: "Bold on-screen text, a quick zoom-in, and a hand throwing something away or pushing it off-frame." },
    secret:   { label: "Insider secret", emotion: "Curiosity gap",
                visual: "Lean in like you're sharing a secret. Show the product or result in the last half second only." },
    proof:    { label: "Social proof", emotion: "Trust / envy",
                visual: "Show the result first (the thing people ask about), then pan or cut to the product." },
    result:   { label: "Result / timeline", emotion: "Anticipation",
                visual: "Split-screen or a day counter on screen. Show the 'before' in the first frame." },
    urgency:  { label: "Urgency / FOMO", emotion: "FOMO",
                visual: "Fast energy. Show the product stack or cart, point at the screen, add a countdown or 'low stock' text." },
    contrarian:{label: "Contrarian take", emotion: "Intrigue",
                visual: "Deadpan delivery. Shake your head slightly at the 'old way' item, then bring in the product." }
  };

  /* ---------- Hook templates ----------
     {audience} {pain} {benefit} {product} {noun}; {Audience} etc. capitalise the first letter.
     `t` = spoken line. `text` = shorter on-screen text version. */
  const TEMPLATES = [
    // callout
    { type: "callout", t: "If you're one of the {audience} dealing with {pain}, stop scrolling.", text: "{Audience} with {pain}? Watch this" },
    { type: "callout", t: "{Audience}, this one's for you if you're sick of {pain}.", text: "{Audience}: this is for you" },
    { type: "callout", t: "Calling all {audience} who are sick of {pain}.", text: "Sick of {pain}?" },
    // question
    { type: "question", t: "Why is nobody talking about this fix for {pain}?", text: "Why is nobody talking about this?" },
    { type: "question", t: "What if {pain} wasn't something you just had to live with?", text: "What if {pain} wasn't permanent?" },
    { type: "question", t: "{Audience}, are you still putting up with {pain}?", text: "Still dealing with {pain}?" },
    // confession
    { type: "confession", t: "I was so tired of {pain} until I found {product}.", text: "I was SO over {pain}" },
    { type: "confession", t: "I almost gave up on {pain}. Then this showed up.", text: "I almost gave up…" },
    { type: "confession", t: "Okay, I'm obsessed. {product} actually helped with {pain}.", text: "Okay I'm obsessed" },
    // pov
    { type: "pov", t: "POV: you finally found something that fixes {pain}.", text: "POV: you fixed {pain}" },
    { type: "pov", t: "POV: you're one of the {audience} who just discovered {product}.", text: "POV: you found {product}" },
    // shock
    { type: "shock", t: "Stop wasting money on stuff that doesn't fix {pain}.", text: "Stop wasting money on {pain}" },
    { type: "shock", t: "Please don't buy another {noun} before you watch this.", text: "Don't buy another {noun}" },
    { type: "shock", t: "I can't believe I put up with {pain} for this long.", text: "I put up with {pain} for WHAT" },
    // secret
    { type: "secret", t: "The {noun} {audience} keep sleeping on.", text: "{Audience} keep sleeping on this" },
    { type: "secret", t: "This is the {noun} hack I wish I knew sooner.", text: "The hack I wish I knew sooner" },
    // proof
    { type: "proof", t: "Everyone keeps asking how I got {benefit}. It's this.", text: "How I got {benefit}" },
    { type: "proof", t: "This {noun} has been blowing up, and now I get why.", text: "I get the hype now" },
    // result
    { type: "result", t: "I used {product} for seven days. Here's what happened with {pain}.", text: "7 days of {product}" },
    { type: "result", t: "Day one versus day fourteen: {benefit}.", text: "Day 1 vs day 14" },
    // urgency
    { type: "urgency", t: "{product} just restocked and it will not last.", text: "JUST RESTOCKED" },
    { type: "urgency", t: "If you're fighting {pain}, grab this before it sells out again.", text: "Grab it before it's gone" },
    // contrarian
    { type: "contrarian", t: "Unpopular opinion: the {noun} you're using is why you still have {pain}.", text: "Unpopular opinion" },
    { type: "contrarian", t: "You don't need a bigger routine. You need {product}.", text: "You don't need more. You need this" }
  ];

  /* ---------- Script parts (Hook → Problem → Solution → CTA) ---------- */
  const PROBLEMS = [
    "Honestly, {pain} has been such a struggle for me. I tried everything and nothing really worked.",
    "If you deal with {pain}, you know how frustrating it gets. I was at the point where I'd try anything.",
    "I kept running into {pain} no matter what I changed, and it was driving me crazy."
  ];
  const SOLUTIONS = [
    "That's when I tried {product}. Within a week I noticed {benefit}, and I haven't gone back.",
    "{product} is what finally worked for me. It's the reason I have {benefit} now.",
    "So I switched to {product}, and the difference was obvious. {BenefitCap}, without the hassle."
  ];
  const CTAS = {
    sale:     "It's on sale right now. Tap the link and grab it before the price goes back up.",
    restock:  "It just restocked, and it sells out fast. Tap the link and grab yours now.",
    launch:   "It literally just launched. Tap the link and be one of the first to try it.",
    bundle:   "They've got a bundle deal going right now, so it's cheaper than buying one. Link's below.",
    shipping: "Right now there's free shipping, so there's no better time. Tap the link.",
    custom:   "{offer} Tap the link below.",
    none:     "If this sounds like you, tap the link below and check it out."
  };
  const CTA_ONSCREEN = {
    sale: "SALE ENDS SOON", restock: "JUST RESTOCKED", launch: "NEW DROP",
    bundle: "BUNDLE DEAL", shipping: "FREE SHIPPING", custom: "{offer}", none: "LINK BELOW"
  };

  /* ---------- Engine ---------- */
  const cap = s => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
  const pick = arr => arr[Math.floor(Math.random() * arr.length)];
  const lines = s => (s || "").split(/\n/).map(x => x.trim()).filter(Boolean);

  function fill(tpl, v) {
    return tpl
      .replace(/\{(\w+)\}/g, (m, key) => {
        if (key === "BenefitCap") return cap(v.benefit);
        if (key === "Audience") return cap(v.audience);
        if (key === "Pain") return cap(v.pain);
        return v[key] != null ? v[key] : m;
      })
      .replace(/\s+([.,!?:])/g, "$1")
      .replace(/\s{2,}/g, " ")
      .trim();
  }

  /* inputs: { product, category, audiences:[], pains:[], benefits:[], types:[], offer, offerType }
     returns array of hook objects. */
  function buildHook(tpl, inp) {
    const cat = CATEGORIES[inp.category] || CATEGORIES.general;
    const vars = {
      product: inp.product || "this",
      noun: cat.noun,
      audience: pick(inp.audiences.length ? inp.audiences : cat.audiences),
      pain: pick(inp.pains.length ? inp.pains : cat.pains),
      benefit: pick(inp.benefits.length ? inp.benefits : cat.benefits)
    };
    const type = HOOK_TYPES[tpl.type];
    return {
      id: Math.random().toString(36).slice(2, 9),
      type: tpl.type, typeLabel: type.label, emotion: type.emotion,
      tplText: tpl.t, tplScreen: tpl.text,
      vars,
      spoken: fill(tpl.t, vars),
      onscreen: fill(tpl.text, vars),
      visual: type.visual,
      broll: pick(cat.visuals)
    };
  }

  function generate(inp, perType) {
    perType = perType || 2;
    const types = inp.types && inp.types.length ? inp.types : Object.keys(HOOK_TYPES);
    const out = [];
    types.forEach(tp => {
      const pool = TEMPLATES.filter(t => t.type === tp).sort(() => Math.random() - 0.5);
      pool.slice(0, perType).forEach(tpl => out.push(buildHook(tpl, inp)));
    });
    return out;
  }

  // Reroll a single hook: same type, different template when possible.
  function reroll(hook, inp) {
    const pool = TEMPLATES.filter(t => t.type === hook.type);
    const others = pool.filter(t => t.t !== hook.tplText);
    return buildHook(pick(others.length ? others : pool), inp);
  }

  function buildScript(hook, inp) {
    const v = hook.vars;
    const offerType = inp.offerType || "none";
    const offerVars = Object.assign({}, v, { offer: (inp.offer || "").trim() });
    const ctaTpl = CTAS[offerType] || CTAS.none;
    const ctaText = offerType === "custom" && !offerVars.offer ? CTAS.none : ctaTpl;
    const screenCta = offerType === "custom" && !offerVars.offer ? CTA_ONSCREEN.none : CTA_ONSCREEN[offerType];
    return {
      hook:     { say: hook.spoken, show: hook.visual + " B-roll idea: " + hook.broll + ".", text: hook.onscreen },
      problem:  { say: fill(pick(PROBLEMS), v), show: "Show the problem happening for real: the mess, the frustration, the bad result.", text: cap(v.pain) },
      solution: { say: fill(pick(SOLUTIONS), v), show: "Product enters frame. Demo the one feature that solves it. Show the proof shot (result).", text: cap(v.benefit) },
      cta:      { say: fill(ctaText, offerVars), show: "Hold the product up, point toward the link/cart, smile.", text: fill(screenCta, offerVars) }
    };
  }

  const API = { CATEGORIES, HOOK_TYPES, TEMPLATES, generate, reroll, buildScript, lines, cap };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.HookLab = API;
})(typeof window !== "undefined" ? window : globalThis);
