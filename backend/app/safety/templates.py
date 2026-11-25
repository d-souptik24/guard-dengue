"""
GuardDengue — Pre-compiled Clinical Safety Templates (Zone 2)

Curated, medically verified static responses for emergency bypasses,
contraindicated NSAID intercepts, and chronic prescription guidance.
These responses bypass generative inference completely with zero latency.
"""

# ─── 1. Emergency Red Flag Bypass Templates ──────────────────────────────────
EMERGENCY_RED_FLAG_EN = (
    "🚨 **EMERGENCY WARNING: SEEK IMMEDIATE HOSPITAL CARE**\n\n"
    "Based on the warning signs you reported (such as severe abdominal pain, persistent vomiting, bleeding, or extreme lethargy), "
    "this patient is at high risk of progressing to **Severe Dengue (Dengue Shock Syndrome / Dengue Hemorrhagic Fever)**.\n\n"
    "**Immediate Actions Required:**\n\n"
    "1. **Call 108 immediately** for an emergency ambulance or proceed to the nearest hospital emergency department without delay.\n"
    "2. Keep the patient lying down and resting quietly.\n"
    "3. Do not give large volumes of plain water quickly if vomiting.\n"
    "4. **DO NOT administer pain relievers like Aspirin, Ibuprofen, Combiflam, or Diclofenac**, as these dramatically worsen internal bleeding.\n\n"
    "*Time is critical. Please seek professional emergency medical evaluation immediately.*"
)

EMERGENCY_RED_FLAG_BN = (
    "🚨 **জরুরী সতর্কতা: অবিলম্বে হাসপাতালে যান**\n\n"
    "আপনি যে বিপজ্জনক লক্ষণগুলির কথা উল্লেখ করেছেন (যেমন তীব্র পেটে ব্যথা, অবিরাম বমি, রক্তপাত, বা চরম দুর্বলতা/নিস্তেজ ভাব), "
    "তা **মারাত্মক ডেঙ্গু (Dengue Shock Syndrome)** এর পূর্বলক্ষণ হতে পারে।\n\n"
    "**অবিলম্বে করণীয়:**\n\n"
    "1. **অবিলম্বে ১০৮ নম্বরে কল করুন** অথবা রোগীকে কালবিলম্ব না করে নিকটস্থ সরকারি বা বেসরকারি হাসপাতালের জরুরি বিভাগে নিয়ে যান।\n"
    "2. রোগীকে পূর্ণ বিশ্রামে রাখুন।\n"
    "3. রোগীকে জোর করে অতিরিক্ত জল পান করাবেন না যদি অবিরাম বমি হতে থাকে।\n"
    "4. **ভুল করেও ব্রুফেন (Ibuprofen), অ্যাসপিরিন (Aspirin), কম্বিফ্লাম (Combiflam), বা ডাইক্লোফেনাক জাতীয় ব্যথানাশক ওষুধ খাওয়াবেন না**। এগুলি রক্তক্ষরণ বাড়িয়ে রোগীর জীবন সংশয় করতে পারে।\n\n"
    "*সময় খুবই মূল্যবান। দয়া করে অবিলম্বে চিকিৎসকের শরণাপন্ন হন।*"
)

# ─── 2. NSAID Contraindication Intercept Templates ────────────────────────────
NSAID_CONTRAINDICATION_EN = (
    "⛔ **CRITICAL MEDICATION WARNING: DO NOT TAKE {drug_name}**\n\n"
    "**Non-Steroidal Anti-Inflammatory Drugs (NSAIDs)** such as **{drug_name}** (as well as Ibuprofen, Aspirin, Combiflam, Diclofenac, Naproxen, and Meftal) "
    "are **strictly contraindicated** in dengue fever.\n\n"
    "**Why is it dangerous?**\n\n"
    "Dengue causes capillary fragility and platelet destruction. NSAIDs inhibit platelet aggregation and damage the gastric lining, "
    "which drastically multiplies the risk of severe gastrointestinal hemorrhage and life-threatening internal bleeding.\n\n"
    "**Safe Alternative:**\n\n"
    "- **Paracetamol** (Acetaminophen) is the antipyretic of choice for fever and body aches in dengue, taken strictly within prescribed dosing limits (consult your doctor or pharmacist).\n"
    "- Keep well hydrated with Oral Rehydration Salts (ORS), coconut water, and fluids."
)

NSAID_CONTRAINDICATION_BN = (
    "⛔ **জরুরী ওষুধ সতর্কতা: {drug_name} সেবন করবেন না**\n\n"
    "ডেঙ্গু জ্বরে **{drug_name}** (এবং ব্রুফেন, অ্যাসপিরিন, কম্বিফ্লাম, ডাইক্লোফেনাক, মেফট্যাল ইত্যাদি NSAID ব্যথানাশক ওষুধ) "
    "খাওয়া **সম্পূর্ণ নিষিদ্ধ ও অত্যন্ত বিপজ্জনক**।\n\n"
    "**কেন এটি ক্ষতিকর?**\n\n"
    "ডেঙ্গু ভাইরাস রক্তে প্লাটিলেট কমিয়ে দেয় এবং রক্তনালীর ক্ষতি করে। এই জাতীয় ব্যথানাশক ওষুধ প্লাটিলেট জমতে বাধা দেয় এবং পেটে আলসার সৃষ্টি করে, "
    "যার ফলে মারাত্মক অভ্যন্তরীণ রক্তক্ষরণ (Internal Bleeding) হওয়ার প্রবল ঝুঁকি তৈরি হয়।\n\n"
    "**নিরাপদ বিকল্প:**\n\n"
    "- জ্বর ও ব্যথার জন্য শুধুমাত্র **প্যারাসিটামল (Paracetamol)** সেবন করা উচিত, চিকিৎসকের পরামর্শ অনুযায়ী সঠিক মাত্রায়।\n"
    "- প্রচুর পরিমাণে ওআরএস (ORS), ডাবের জল ও তরল খাবার গ্রহণ করুন।"
)

# ─── 3. Chronic Prescription Caveat Templates ─────────────────────────────────
NSAID_CHRONIC_RX_EN = (
    "⚠️ **IMPORTANT NOTICE REGARDING REGULAR / CARDIAC MEDICATIONS**\n\n"
    "You mentioned taking **{drug_name}**, which appears to be part of a long-term medical prescription (such as daily cardiac aspirin or blood thinners).\n\n"
    "- **Do NOT abruptly stop or alter your prescribed daily medication on your own.**\n"
    "- Contact your treating cardiologist, physician, or hospital immediately and inform them that you suspect or have dengue.\n"
    "- Your doctor will balance your thrombotic/cardiovascular risk against dengue hemorrhagic risk and provide supervised medical guidance."
)

NSAID_CHRONIC_RX_BN = (
    "⚠️ **নিয়মিত বা হৃদরোগের ওষুধের ক্ষেত্রে বিশেষ সতর্কতা**\n\n"
    "আপনি যে ওষুধটির কথা বলেছেন (**{drug_name}**), তা যদি আপনার চিকিৎসক কোনো দীর্ঘমেয়াদী রোগ বা হৃদরোগের জন্য প্রেসক্রাইব করে থাকেন:\n\n"
    "- **নিজের সিদ্ধান্তে কখনোই প্রেসক্রিপশনের ওষুধ হঠাৎ বন্ধ বা পরিবর্তন করবেন না।**\n"
    "- অবিলম্বে আপনার হৃদরোগ বিশেষজ্ঞ বা চিকিৎসকের সাথে যোগাযোগ করে জানান যে আপনার ডেঙ্গুর লক্ষণ বা সংক্রমণ রয়েছে।\n"
    "- চিকিৎসক আপনার সামগ্রিক স্বাস্থ্য পরীক্ষা করে নিরাপদ ব্যবস্থা নির্ধারণ করবেন।"
)

# ─── 4. Out-of-Scope / Uncertain Templates ───────────────────────────────────
ABSTAIN_UNCERTAIN_EN = (
    "I can only provide guidance related to Dengue fever, its clinical warning signs, diagnostic timelines, and medication safety. "
    "Your query does not appear to match dengue clinical management guidelines, or there is insufficient authoritative clinical evidence to provide a safe answer. "
    "Please consult a certified medical practitioner or qualified healthcare center for personalized advice."
)

ABSTAIN_UNCERTAIN_BN = (
    "আমি শুধুমাত্র ডেঙ্গু জ্বর, এর সতর্কতামূলক লক্ষণ, ল্যাব পরীক্ষা ও ওষুধ সংক্রান্ত সরকারি স্বাস্থ্য নির্দেশিকা সম্পর্কিত তথ্য প্রদান করতে পারি। "
    "আপনার প্রশ্নটি ডেঙ্গু স্বাস্থ্য নির্দেশিকার আওতাভুক্ত নয় অথবা এর নির্ভরযোগ্য প্রমাণ পাওয়া যায়নি। "
    "অনুগ্রহ করে সঠিক চিকিৎসার জন্য নিকটস্থ স্বাস্থ্যকেন্দ্র বা চিকিৎসকের পরামর্শ নিন।"
)

# ─── 5. Universal Safety Disclaimers ─────────────────────────────────────────
DISCLAIMER_EN = (
    "GuardDengue provides algorithmic clinical decision support based on WHO (2024), NCVBDC, and ICMR guidelines. "
    "This does not substitute for certified clinical diagnosis or medical treatment. In any emergency, dial 108 immediately."
)

DISCLAIMER_BN = (
    "গার্ডডেঙ্গু হু (WHO ২০২৪), এনসিভিবিডিসি এবং আইসিএমআর নির্দেশিকার ভিত্তিতে তথ্য প্রদান করে। "
    "এটি কোনো নিবন্ধিত চিকিৎসকের বিকল্প নয়। যেকোনো জরুরী পরিস্থিতিতে অবিলম্বে ১০৮ নম্বরে ফোন করুন।"
)
