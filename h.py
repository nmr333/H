"""
Personal micronutrient & macronutrient estimator
Author: ChatGPT
Usage: Run in Python 3. Requires only standard libraries (pandas optionally).
Outputs estimated daily needs for macros + common vitamins & minerals.
Notes: Values are approximate adult RDAs/AI (general population). Consult a clinician for cases like pregnancy, disease, medications.
"""

from math import floor

try:
    import pandas as pd
except Exception:
    pd = None

def input_or_default(prompt, default=None, cast=str):
    v = input(f"{prompt} " + (f"[default: {default}]: " if default is not None else ": "))
    if v.strip() == "" and default is not None:
        return default
    try:
        return cast(v)
    except Exception:
        print("Invalid input, using default.")
        return default

def get_user_data():
    print("أدخل بياناتك (اضغط Enter لاستخدام القيمة الافتراضية إن وُجدت):")
    sex = input_or_default("الجنس (male/female)", "male", str).strip().lower()
    age = input_or_default("العمر (سنة)", 30, int)
    weight = input_or_default("الوزن (كجم)", 70.0, float)
    height = input_or_default("الطول (سم)", 175.0, float)
    body_fat = input_or_default("نسبة الدهون (%) — اتركها فارغة إذا لا تعرف", "", str)
    try:
        body_fat = float(body_fat) if body_fat != "" else None
    except:
        body_fat = None
    activity = input_or_default("مستوى النشاط (sedentary, light, moderate, active, very_active)", "light", str)
    goal = input_or_default("الهدف (maintain, lose, gain)", "maintain", str)
    menstruating = False
    pregnant = False
    breastfeeding = False
    if sex == "female":
        m = input_or_default("هل لديك دورة شهرية طبيعية؟ (yes/no)", "yes", str).strip().lower()
        menstruating = (m == "yes")
        p = input_or_default("هل أنت حامل؟ (yes/no)", "no", str).strip().lower()
        pregnant = (p == "yes")
        b = input_or_default("هل ترضعين؟ (yes/no)", "no", str).strip().lower()
        breastfeeding = (b == "yes")
    notes = input_or_default("ملاحظات طبية/أدوية (اختياري)", "", str)
    return {
        "sex": sex,
        "age": age,
        "weight": weight,
        "height": height,
        "body_fat": body_fat,
        "activity": activity,
        "goal": goal,
        "menstruating": menstruating,
        "pregnant": pregnant,
        "breastfeeding": breastfeeding,
        "notes": notes
    }

# BMR (Mifflin-St Jeor)
def calc_bmr(sex, weight, height, age):
    if sex == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

activity_factors = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9
}

def calc_tdee(bmr, activity, goal):
    factor = activity_factors.get(activity, 1.375)
    tdee = bmr * factor
    if goal == "lose":
        tdee *= 0.85  # ~15% deficit
    elif goal == "gain":
        tdee *= 1.10  # ~10% surplus
    return tdee

# Macro rules (simple heuristics)
def calc_macros(weight, activity, goal):
    # protein: baseline 0.8 g/kg, adjust up for activity/goal
    base_protein = 0.8
    if activity in ("moderate", "active", "very_active"):
        base_protein = 1.2
    if goal == "gain":
        base_protein += 0.3
    if goal == "lose":
        base_protein += 0.2
    protein_g = round(base_protein * weight, 1)

    # fats: 25-35% of calories, pick 30% of TDEE as kcal from fat
    # carbs: remaining calories
    return {"protein_g_per_day": protein_g, "protein_g_per_kg": round(base_protein,2)}

# Core micronutrient RDAs/AI for adults (approximate)
# Units: mg unless otherwise specified. Comments include units.
# Values are typical adult (19-50) — some adjust for sex/menstruation/pregnancy.
def base_micronutrient_table(sex, age, menstruating=False, pregnant=False, breastfeeding=False):
    # We'll return dict: nutrient -> (value, unit, note)
    d = {}
    # Vitamins
    if sex == "male":
        d["Vitamin A"] = (900, "µg RAE", "Adult male RDA")
        d["Vitamin C"] = (90, "mg", "")
        d["Vitamin D"] = (15, "µg (600 IU)", "")
        d["Vitamin E"] = (15, "mg", "")
        d["Vitamin K"] = (120, "µg", "")
        d["Thiamin (B1)"] = (1.2, "mg", "")
        d["Riboflavin (B2)"] = (1.3, "mg", "")
        d["Niacin (B3)"] = (16, "mg NE", "")
        d["Vitamin B6"] = (1.3, "mg", "may increase with age")
        d["Folate (B9)"] = (400, "µg DFE", "")
        d["Vitamin B12"] = (2.4, "µg", "")
        d["Pantothenic acid (B5)"] = (5, "mg", "")
        d["Biotin (B7)"] = (30, "µg", "")
    else:
        d["Vitamin A"] = (700, "µg RAE", "Adult female RDA")
        d["Vitamin C"] = (75, "mg", "")
        d["Vitamin D"] = (15, "µg (600 IU)", "")
        d["Vitamin E"] = (15, "mg", "")
        d["Vitamin K"] = (90, "µg", "")
        d["Thiamin (B1)"] = (1.1, "mg", "")
        d["Riboflavin (B2)"] = (1.1, "mg", "")
        d["Niacin (B3)"] = (14, "mg NE", "")
        d["Vitamin B6"] = (1.3, "mg", "")
        d["Folate (B9)"] = (400, "µg DFE", "")
        d["Vitamin B12"] = (2.4, "µg", "")
        d["Pantothenic acid (B5)"] = (5, "mg", "")
        d["Biotin (B7)"] = (30, "µg", "")

    # Minerals
    if sex == "male":
        d["Calcium"] = (1000, "mg", "Adults 19-50")
        d["Iron"] = (8, "mg", "Men")
        d["Magnesium"] = (400, "mg", "Adult male")
        d["Phosphorus"] = (700, "mg", "")
        d["Potassium"] = (3400, "mg", "AI")
        d["Sodium"] = (1500, "mg", "AI (upper limits higher)")
        d["Zinc"] = (11, "mg", "")
        d["Copper"] = (0.9, "mg", "")
        d["Manganese"] = (2.3, "mg", "")
        d["Selenium"] = (55, "µg", "")
        d["Chromium"] = (35, "µg", "")
        d["Iodine"] = (150, "µg", "")
        d["Fluoride"] = (4, "mg", "AI")
    else:
        d["Calcium"] = (1000, "mg", "Adults 19-50")
        d["Iron"] = (18, "mg", "Women of reproductive age")
        d["Magnesium"] = (310, "mg", "Adult female")
        d["Phosphorus"] = (700, "mg", "")
        d["Potassium"] = (2600, "mg", "AI")
        d["Sodium"] = (1500, "mg", "AI (upper limits higher)")
        d["Zinc"] = (8, "mg", "")
        d["Copper"] = (0.9, "mg", "")
        d["Manganese"] = (1.8, "mg", "")
        d["Selenium"] = (55, "µg", "")
        d["Chromium"] = (25, "µg", "")
        d["Iodine"] = (150, "µg", "")
        d["Fluoride"] = (3, "mg", "AI")

    # Adjustments for menstruation/pregnancy/breastfeeding
    if menstruating and sex == "female":
        # ensure iron need remains high (already set to 18 mg)
        d["Iron"] = (18, "mg", "Increased due to menstrual losses")
    if pregnant and sex == "female":
        # increase some needs
        d["Folate (B9)"] = (600, "µg DFE", "Pregnancy increased need")
        d["Iron"] = (27, "mg", "Pregnancy increased need")
        d["Calcium"] = (1000, "mg", "Pregnancy recommendation")
        d["Vitamin D"] = (15, "µg (600 IU)", "May be increased based on status")
        d["Iodine"] = (220, "µg", "Pregnancy increased need")
    if breastfeeding and sex == "female":
        d["Folate (B9)"] = (500, "µg DFE", "Lactation increased need")
        d["Iron"] = (9, "mg", "Postpartum needs lower than pregnancy")
        d["Vitamin D"] = (15, "µg (600 IU)", "")
        d["Iodine"] = (290, "µg", "Lactation increased need")
    return d

def pretty_print_results(user, bmr, tdee, macros, micro_table):
    print("\n--- النتائج التقديرية اليومية ---\n")
    print(f"الوزن: {user['weight']} كجم | الطول: {user['height']} سم | العمر: {user['age']} | الجنس: {user['sex']}")
    if user['body_fat'] is not None:
        lbm = user['weight'] * (1 - user['body_fat']/100.0)
        print(f"نسبة الدهون: {user['body_fat']}%  → كتلة الجسم الخالية من الدهون (تقريبية): {lbm:.1f} كجم")
    print(f"\nBMR (حرق الراحة): {bmr:.0f} kcal/day")
    print(f"TDEE (بعد النشاط والهدف): {tdee:.0f} kcal/day\n")
    print("المغذيات الكبرى (تقريبية):")
    print(f" • بروتين: {macros['protein_g_per_day']} غرام/يوم  (~{macros['protein_g_per_kg']} غ/كجم)")
    # fat and carbs estimate based on percentages of TDEE
    fat_kcal = tdee * 0.30
    fat_g = fat_kcal / 9
    carbs_kcal = tdee - (macros['protein_g_per_day'] * 4) - fat_kcal
    carbs_g = max(0, carbs_kcal / 4)
    print(f" • دهون: {fat_g:.1f} غرام/يوم  (~30% من السعرات)")
    print(f" • كربوهيدرات: {carbs_g:.1f} غرام/يوم\n")

    # micronutrients table
    rows = []
    for nut, (val, unit, note) in micro_table.items():
        rows.append({"Nutrient": nut, "Daily need": f"{val} {unit}", "Note": note})
    if pd:
        df = pd.DataFrame(rows)
        print("== جدول الفيتامينات والمعادن (تقديري) ==\n")
        display_df = df.set_index("Nutrient")
        print(display_df.to_string())
    else:
        print("== جدول الفيتامينات والمعادن (تقديري) ==\n")
        for r in rows:
            print(f"{r['Nutrient']:<25} : {r['Daily need']:<18} | {r['Note']}")

    print("\nملاحظات:")
    print("- القيم تقريبية للاشخاص البالغين الأصحاء. للحالات الخاصة (أمراض، أدوية، حمل، رضاع) استشر أخصائي تغذية.")
    print("- الحديد مهم للنساء في سن الإنجاب، تم رفع القيمة بالنسبة للنساء ذوات الطمث المنتظم.")
    print("- فيتامين D قد يحتاج لفحص الدم/تعويض إذا كان التعرض للشمس منخفضًا.")
    print("- يمكنك حفظ النتائج لاحقًا أو تعديل المعايير بسهولة في الكود.")

def main():
    user = get_user_data()
    bmr = calc_bmr(user['sex'], user['weight'], user['height'], user['age'])
    tdee = calc_tdee(bmr, user['activity'], user['goal'])
    macros = calc_macros(user['weight'], user['activity'], user['goal'])
    micro = base_micronutrient_table(user['sex'], user['age'], user['menstruating'], user['pregnant'], user['breastfeeding'])
    pretty_print_results(user, bmr, tdee, macros, micro)

if __name__ == "__main__":
    main()
