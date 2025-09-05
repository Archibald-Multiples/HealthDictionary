"""
Script to add new healthcare terms to the database only if they do not already exist.
"""

from app import app, db
from models import Category, Term
import pandas as pd
from datetime import datetime
from models import Category, Term
from datetime import datetime

# List of new terms to add (example: add more as needed)
NEW_TERMS = [
    # BODY PARTS
    {"term_en": "Heart", "term_ewe": "Dzi", "definition_en": "The organ that pumps blood", "definition_ewe": "Nu si nɔa ʋu ɖom", "example_en": "Feel your heart beating", "example_ewe": "Se wò dzi ƒe ƒoƒo", "category_name_en": "Body Parts"},
    {"term_en": "Head", "term_ewe": "Ta", "definition_en": "The upper part of the body", "definition_ewe": "Ŋutilã ƒe tame", "example_en": "My head hurts", "example_ewe": "Nye ta le vevem", "category_name_en": "Body Parts"},
    {"term_en": "Hand", "term_ewe": "Asi", "definition_en": "The body part used for grasping", "definition_ewe": "Ŋutilã ƒe akpa si wotsɔna lɔa nu", "example_en": "Wash your hands", "example_ewe": "Klɔ wò asiwo", "category_name_en": "Body Parts"},
    {"term_en": "Eye", "term_ewe": "Ŋku", "definition_en": "The organ of sight", "definition_ewe": "Nukpɔnu", "example_en": "Check your eyes regularly", "example_ewe": "Kpɔ wò ŋkuwo ɖa kabakaba", "category_name_en": "Body Parts"},
    {"term_en": "Ear", "term_ewe": "To", "definition_en": "The organ of hearing", "definition_ewe": "Nuseenu", "example_en": "Clean your ears gently", "example_ewe": "Klɔ wò towo blewuu", "category_name_en": "Body Parts"},
    {"term_en": "Nose", "term_ewe": "Ŋɔti", "definition_en": "The organ of smell", "definition_ewe": "Nuʋeʋẽnu", "example_en": "Breathe through your nose", "example_ewe": "Gbɔ agbɔ to wò ŋɔti me", "category_name_en": "Body Parts"},
    {"term_en": "Mouth", "term_ewe": "Nu", "definition_en": "The opening for eating and speaking", "definition_ewe": "Nuɖuɖu kple nuƒoƒonu", "example_en": "Keep your mouth clean", "example_ewe": "Na wò nu nanɔ dzadzɛe", "category_name_en": "Body Parts"},
    {"term_en": "Stomach", "term_ewe": "Fo", "definition_en": "The organ that digests food", "definition_ewe": "Nu si gblẽa nuɖuɖu", "example_en": "My stomach is upset", "example_ewe": "Nye fo me le nyam", "category_name_en": "Body Parts"},
    # DISEASES
    {"term_en": "Fever", "term_ewe": "Asrã", "definition_en": "High body temperature", "definition_ewe": "Ŋutilã ƒe dzoxɔxɔ kɔkɔ", "example_en": "The patient has fever", "example_ewe": "Asrã le dɔnɔ la ŋu", "category_name_en": "Diseases"},
    {"term_en": "Headache", "term_ewe": "Taʋeʋe", "definition_en": "Pain in the head", "definition_ewe": "Vevesese le ta me", "example_en": "I have a severe headache", "example_ewe": "Taʋeʋe sesẽ aɖe le dzinye", "category_name_en": "Diseases"},
    {"term_en": "Medicine", "term_ewe": "Atike", "definition_en": "Substance used to treat illness", "definition_ewe": "Nu si wotsɔna doa dɔ", "example_en": "Take your medicine daily", "example_ewe": "No wò atike gbe sia gbe", "category_name_en": "Diseases"},
    {"term_en": "Diabetes", "term_ewe": "Suklidɔ", "definition_en": "Disease affecting blood sugar", "definition_ewe": "Dɔ si kaa sukli le ʋu me", "example_en": "Monitor your diabetes daily", "example_ewe": "Kpɔ wò suklidɔ ɖa gbe sia gbe", "category_name_en": "Diseases"},
    {"term_en": "Hypertension", "term_ewe": "Ʋunyanyra", "definition_en": "High blood pressure", "definition_ewe": "Ʋu ƒe nyanyram kɔkɔ", "example_en": "Control your hypertension", "example_ewe": "Ɖu wò ʋunyanyra dzi", "category_name_en": "Diseases"},
    {"term_en": "Malaria", "term_ewe": "Ƒodɔ", "definition_en": "Disease spread by mosquitoes", "definition_ewe": "Dɔ si yitiwo kakana", "example_en": "Malaria causes fever", "example_ewe": "Ƒodɔ henaa asrã", "category_name_en": "Diseases"},
    {"term_en": "Tuberculosis", "term_ewe": "Ƒodo", "definition_en": "Lung infection disease", "definition_ewe": "Dɔ si kaa ƒodo", "example_en": "TB treatment takes months", "example_ewe": "Ƒodo ƒe dɔyɔyɔ xɔa ɣleti geɖewo", "category_name_en": "Diseases"},
    {"term_en": "Asthma", "term_ewe": "Gbɔgbɔdɔ", "definition_en": "Breathing difficulty disease", "definition_ewe": "Dɔ si wɔnɛ be gbɔgbɔciɖeɖe sesẽna", "example_en": "Use your asthma inhaler", "example_ewe": "Zã wò gbɔgbɔdɔ ƒe atike", "category_name_en": "Diseases"},
    # SYMPTOMS
    {"term_en": "Pain", "term_ewe": "Vevesese", "definition_en": "Unpleasant physical sensation", "definition_ewe": "Ŋutilã ƒe nuvevesese", "example_en": "Where is the pain?", "example_ewe": "Vevesese la le afi ka?", "category_name_en": "Symptoms"},
    {"term_en": "Cough", "term_ewe": "Ƒedɔ", "definition_en": "Forceful expulsion of air from lungs", "definition_ewe": "Gbɔgbɔ sesẽ ɖeɖe tso ƒodo me", "example_en": "The cough is getting worse", "example_ewe": "Ƒedɔ la le sesẽm ɖe edzi", "category_name_en": "Symptoms"},
    {"term_en": "Swelling", "term_ewe": "Tetekpɔ", "definition_en": "Abnormal enlargement of body part", "definition_ewe": "Ŋutilã ƒe akpa aɖe ƒe tutu si meɖoa kpe ɖe nu o", "example_en": "There is swelling in the leg", "example_ewe": "Tetekpɔ le afɔ la ŋu", "category_name_en": "Symptoms"},
    {"term_en": "Nausea", "term_ewe": "Ɖiɖi", "definition_en": "Feeling sick to stomach", "definition_ewe": "Susu be yeɖe nu ada", "example_en": "I have nausea", "example_ewe": "Ɖiɖi le dzinye", "category_name_en": "Symptoms"},
    {"term_en": "Vomiting", "term_ewe": "Nuɖeɖe", "definition_en": "Throwing up food", "definition_ewe": "Nuɖuɖu ƒe ɖeɖe", "example_en": "Stop eating if vomiting", "example_ewe": "Dzudzɔ nuɖuɖu ne èle nu ɖem", "category_name_en": "Symptoms"},
    {"term_en": "Diarrhea", "term_ewe": "Afɔku", "definition_en": "Loose bowel movements", "definition_ewe": "Afɔ ƒe kuku", "example_en": "Drink fluids for diarrhea", "example_ewe": "No tsi ne afɔku le asiwò", "category_name_en": "Symptoms"},
    {"term_en": "Dizziness", "term_ewe": "Tanyinyi", "definition_en": "Feeling unsteady", "definition_ewe": "Susu be nu le ɖiɖim", "example_en": "Sit down if dizzy", "example_ewe": "Nɔ anyi ne tanyinyi le dziwò", "category_name_en": "Symptoms"},
    {"term_en": "Chest pain", "term_ewe": "Akɔtaveve", "definition_en": "Pain in the chest area", "definition_ewe": "Vevesese le akɔta", "example_en": "Chest pain needs attention", "example_ewe": "Akɔtaveve hiã kpɔɖeŋu", "category_name_en": "Symptoms"},
    # MEDICATIONS
    {"term_en": "Paracetamol", "term_ewe": "Paracetamol", "definition_en": "Medicine for pain and fever", "definition_ewe": "Atike na vevesese kple asrã", "example_en": "Take paracetamol for fever", "example_ewe": "Tsɔ paracetamol na asrã", "category_name_en": "Medications"},
    {"term_en": "Ibuprofen", "term_ewe": "Ibuprofen", "definition_en": "Anti-inflammatory medicine", "definition_ewe": "Atike si ɖea tetekpɔ kple vevesese", "example_en": "Ibuprofen reduces swelling", "example_ewe": "Ibuprofen ɖea tetekpɔ dzi kpɔtɔna", "category_name_en": "Medications"},
    {"term_en": "Antibiotics", "term_ewe": "Bakteriawuatike", "definition_en": "Medicine that kills bacteria", "definition_ewe": "Atike si wua bakteriawo", "example_en": "Take all antibiotics prescribed", "example_ewe": "Tsɔ bakteriawuatike si wofia wò katã", "category_name_en": "Medications"},
    {"term_en": "Antibiotic", "term_ewe": "Bakteriawuatike", "definition_en": "Medicine that kills bacteria", "definition_ewe": "Atike si wua bakteriawo", "example_en": "Take all antibiotics prescribed", "example_ewe": "Tsɔ bakteriawuatike si wofia wò katã", "category_name_en": "Medications"},
    {"term_en": "Painkiller", "term_ewe": "Vevewuatike", "definition_en": "Medicine for pain relief", "definition_ewe": "Atike si ɖea vevesese ɖa", "example_en": "Use painkillers as directed", "example_ewe": "Zã vevewuatike abe ale si woɖoe da ene", "category_name_en": "Medications"},
    {"term_en": "Vitamin", "term_ewe": "Lãmesesẽnuatike", "definition_en": "Supplement for health", "definition_ewe": "Nu si doa ŋusẽ lãmesesẽ", "example_en": "Take vitamins with food", "example_ewe": "Tsɔ lãmesesẽnuatike kple nuɖuɖu", "category_name_en": "Medications"},
    {"term_en": "Insulin", "term_ewe": "Sukliɖɔɖɔatike", "definition_en": "Medicine for diabetes", "definition_ewe": "Atike na suklidɔ", "example_en": "Store insulin properly", "example_ewe": "Dzra insulin ɖo nyuie", "category_name_en": "Medications"},
    {"term_en": "Cough syrup", "term_ewe": "Ƒedɔatike", "definition_en": "Medicine for cough", "definition_ewe": "Atike na ƒedɔ", "example_en": "Measure cough syrup carefully", "example_ewe": "Dzidze ƒedɔatike nyuie", "category_name_en": "Medications"},
    # MEDICAL PROCEDURES
    {"term_en": "Blood pressure check", "term_ewe": "Ʋunyanyrakpɔkpɔ", "definition_en": "Measuring blood pressure", "definition_ewe": "Ʋu ƒe nyanyram ƒe kpɔkpɔ", "example_en": "Check blood pressure regularly", "example_ewe": "Kpɔ ʋunyanyram edziedzi", "category_name_en": "Medical Procedures"},
    {"term_en": "Temperature check", "term_ewe": "Dzidzɔkpɔkpɔ", "definition_en": "Measuring body temperature", "definition_ewe": "Ŋutilã ƒe dzoxɔxɔ ƒe kpɔkpɔ", "example_en": "Nurse will check temperature", "example_ewe": "Dɔyɔla akpɔ dzoxɔxɔ", "category_name_en": "Medical Procedures"},
    {"term_en": "Prescription", "term_ewe": "Atiketsɔtsɔfiafi", "definition_en": "Written order for medicine", "definition_ewe": "Atike ƒe gbalẽ si wolia na wò", "example_en": "Get prescription from doctor", "example_ewe": "Xɔ atiketsɔtsɔfiafi tso dokta gbɔ", "category_name_en": "Medical Procedures"},
    {"term_en": "X-ray", "term_ewe": "Ƒutakpɔnukɔkɔ", "definition_en": "Picture of bones inside body", "definition_ewe": "Ƒuwo ƒe nɔnɔme le ŋutilã me", "example_en": "X-ray shows broken bones", "example_ewe": "Ƒutakpɔnukɔkɔ ɖea ƒu si ŋe fiana", "category_name_en": "Medical Procedures"},
    {"term_en": "Blood test", "term_ewe": "Ʋukpɔkpɔ", "definition_en": "Testing blood sample", "definition_ewe": "Ʋu ƒe dodokpɔ", "example_en": "Blood test shows health status", "example_ewe": "Ʋukpɔkpɔ ɖea lãmesesẽ ƒe nɔnɔme fiana", "category_name_en": "Medical Procedures"},
    {"term_en": "Surgery", "term_ewe": "Amama", "definition_en": "Operation using tools", "definition_ewe": "Dɔwɔwɔ to dɔwɔnu zazã me", "example_en": "Surgery requires anesthesia", "example_ewe": "Amama hiã aklãmamlɔatike", "category_name_en": "Medical Procedures"},
    {"term_en": "Injection", "term_ewe": "Atikedede", "definition_en": "Medicine given with needle", "definition_ewe": "Atike nana to atikedeti zazã me", "example_en": "Injection may sting briefly", "example_ewe": "Atikedede ate ŋu abi vie", "category_name_en": "Medical Procedures"},
    # MEDICAL EQUIPMENT
    {"term_en": "Stethoscope", "term_ewe": "Dzi ƒe sesenu", "definition_en": "Tool to hear heart and lungs", "definition_ewe": "Nu si wotsɔna sea dzi kple ƒodo", "example_en": "Doctor uses stethoscope", "example_ewe": "Dokta zãa dzi ƒe sesenu", "category_name_en": "Medical Equipment"},
    {"term_en": "Thermometer", "term_ewe": "Dzidzɔmedenu", "definition_en": "Tool to measure temperature", "definition_ewe": "Nu si wotsɔna dzidea dzoxɔxɔ", "example_en": "Check fever with thermometer", "example_ewe": "Tsɔ dzidzɔmedenu kpɔ asrã", "category_name_en": "Medical Equipment"},
    {"term_en": "Syringe", "term_ewe": "Atikededeti", "definition_en": "Tool for giving injections", "definition_ewe": "Nu si wotsɔna dea atike me", "example_en": "Use sterile syringe", "example_ewe": "Zã atikededeti dzadzɛ", "category_name_en": "Medical Equipment"},
    {"term_en": "Wheelchair", "term_ewe": "Amesiametɔ", "definition_en": "Chair with wheels for mobility", "definition_ewe": "Kplɔ̃ si ŋu gaga le na mɔzɔzɔ", "example_en": "Patient needs wheelchair", "example_ewe": "Dɔnɔ hiã amesiametɔ", "category_name_en": "Medical Equipment"},
    {"term_en": "Bandage", "term_ewe": "Ablablabɔ", "definition_en": "Cloth for covering wounds", "definition_ewe": "Avɔ si wotsɔna blana abiwo", "example_en": "Clean bandage prevents infection", "example_ewe": "Ablablabɔ dzadzɛ dea ɖokuibɔ nu", "category_name_en": "Medical Equipment"},
    {"term_en": "Blood pressure cuff", "term_ewe": "Ʋunyanyramedenu", "definition_en": "Tool to measure blood pressure", "definition_ewe": "Nu si wotsɔna dzidea ʋu ƒe nyanyram", "example_en": "Wrap cuff around arm", "example_ewe": "Blɔ ʋunyanyramedenu ɖe abɔ", "category_name_en": "Medical Equipment"},
    {"term_en": "Oxygen tank", "term_ewe": "Gbɔgbɔdanu", "definition_en": "Container with breathing gas", "definition_ewe": "Agba si me gbɔgbɔciɖenu le", "example_en": "Patient needs oxygen", "example_ewe": "Dɔnɔ hiã gbɔgbɔciɖenu", "category_name_en": "Medical Equipment"},
    {"term_en": "Hospital bed", "term_ewe": "Kɔdɔƒeaba", "definition_en": "Special bed for patients", "definition_ewe": "Aba tɔxɛ na dɔnɔwo", "example_en": "Rest in hospital bed", "example_ewe": "Dzudzɔ le kɔdɔƒeaba dzi", "category_name_en": "Medical Equipment"},
]

NEW_TERMS.extend([
  {
    "term_en": "Liver",
    "term_ewe": "Fofo",
    "definition_en": "A large organ that processes nutrients and detoxifies harmful substances.",
    "definition_ewe": "Akpa gã si gblẽa nuɖuɖu kple nusiwo le ame ŋu vɔ̃.",
    "example_en": "The liver filters toxins from the blood.",
    "example_ewe": "Fofo la sĩa vɔ̃nuwo tso ʋu me.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Kidney",
    "term_ewe": "Atu",
    "definition_en": "One of two organs that filter waste from the blood and produce urine.",
    "definition_ewe": "Akpa evea ɖeka si sĩa vɔ̃nuwo tso ʋu me kple tsi wɔna.",
    "example_en": "His kidney function was tested after the infection.",
    "example_ewe": "Wokpɔ eƒe atu ƒe dɔwɔwɔ le dɔvɔ̃ megbe.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Brain",
    "term_ewe": "Taŋu",
    "definition_en": "The organ that controls thought, memory, and bodily functions.",
    "definition_ewe": "Akpa si dɔa susu, ŋkuɖedzesi kple ŋutilã ƒe dɔwo.",
    "example_en": "The brain scan showed no abnormalities.",
    "example_ewe": "Taŋu ƒe kpɔkpɔ la mekpɔ nusi gbegblẽ o.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Pneumonia",
    "term_ewe": "Dzimevɔ̃",
    "definition_en": "An infection that inflames the air sacs in one or both lungs.",
    "definition_ewe": "Dɔvɔ̃ si henaa dzime me yavɔvɔwo le ŋkuɖeɖe me.",
    "example_en": "She was hospitalized for severe pneumonia.",
    "example_ewe": "Wodɔ eŋu le dɔyɔƒe le dzimevɔ̃ sesẽ ŋu.",
    "category_id": 2,
    "category_name_en": "Diseases"
  },
  {
    "term_en": "Hepatitis",
    "term_ewe": "Fofodɔ",
    "definition_en": "Inflammation of the liver, often caused by a virus.",
    "definition_ewe": "Fofo ƒe vɔvɔ, si zɔna va to vailo.",
    "example_en": "Hepatitis B can be prevented with a vaccine.",
    "example_ewe": "Fofodɔ B ate ŋu atsɔ tsidɔkanu le nu.",
    "category_id": 2,
    "category_name_en": "Diseases"
  },
  {
    "term_en": "Arthritis",
    "term_ewe": "Klotidɔ",
    "definition_en": "Inflammation of one or more joints, causing pain and stiffness.",
    "definition_ewe": "Klotiwo ƒe vɔvɔ si hena vevesese kple sesẽ.",
    "example_en": "Arthritis makes it hard for her to walk.",
    "example_ewe": "Klotidɔ wɔnɛ be mɔzɔzɔ sesẽ na esia.",
    "category_id": 2,
    "category_name_en": "Diseases"
  },
  {
    "term_en": "Fatigue",
    "term_ewe": "Dɔlẽ",
    "definition_en": "Extreme tiredness resulting from physical or mental exertion.",
    "definition_ewe": "Dɔlẽ ŋutɔ si va to ŋutilã alo ŋusẽ ƒe dɔwɔwɔ.",
    "example_en": "He felt fatigue after working all day.",
    "example_ewe": "Edzɔ dɔlẽ le dɔwɔwɔ gbeɖe megbe.",
    "category_id": 3,
    "category_name_en": "Symptoms"
  },
  {
    "term_en": "Headache",
    "term_ewe": "Tavese",
    "definition_en": "Pain in the head or neck area.",
    "definition_ewe": "Vevesese le ta alo kɔ me.",
    "example_en": "She took a painkiller for her headache.",
    "example_ewe": "Exɔ vevesedɔati na tavese la.",
    "category_id": 3,
    "category_name_en": "Symptoms"
  },
  {
    "term_en": "Swelling",
    "term_ewe": "Vɔvɔ",
    "definition_en": "An abnormal enlargement of a body part due to fluid buildup.",
    "definition_ewe": "Ŋutilã ƒe akpa ƒe gãɖeɖe si va to tsi ƒe kpekpeɖeŋu.",
    "example_en": "Swelling in her ankle required ice and rest.",
    "example_ewe": "Vɔvɔ le eƒe afɔkpodzi la hiã yɔ kple nɔnɔme.",
    "category_id": 3,
    "category_name_en": "Symptoms"
  },
  {
    "term_en": "Antiviral",
    "term_ewe": "Vailowuatike",
    "definition_en": "A medicine that fights viral infections.",
    "definition_ewe": "Atike si dzea vailo ƒe dɔvɔ̃wo.",
    "example_en": "Antiviral drugs were prescribed for his flu.",
    "example_ewe": "Wofia vailowuatike na eƒe yafɔdɔ.",
    "category_id": 4,
    "category_name_en": "Medications"
  },
  {
    "term_en": "Antihistamine",
    "term_ewe": "Aladzidɔati",
    "definition_en": "A drug that reduces allergic reactions.",
    "definition_ewe": "Atike si ɖea aladzi ƒe nɔnɔme ɖa.",
    "example_en": "She took an antihistamine for her allergies.",
    "example_ewe": "Exɔ aladzidɔati na eƒe aladziwo.",
    "category_id": 4,
    "category_name_en": "Medications"
  },
  {
    "term_en": "Steroid",
    "term_ewe": "Sesẽatike",
    "definition_en": "A drug that reduces inflammation and suppresses the immune system.",
    "definition_ewe": "Atike si ɖea vɔvɔ ɖa kple ŋusẽdzikpɔkpɔ.",
    "example_en": "Steroids helped reduce his joint inflammation.",
    "example_ewe": "Sesẽatike la kpe ɖe eƒe kloti vɔvɔ ŋu.",
    "category_id": 4,
    "category_name_en": "Medications"
  },
  {
    "term_en": "Ultrasound",
    "term_ewe": "Yanuŋkɔkpɔ",
    "definition_en": "A procedure using sound waves to create images of internal organs.",
    "definition_ewe": "Dɔyɔyɔ si tsɔa yanuwɔnuwo wɔa ŋutilã me foto.",
    "example_en": "The ultrasound showed a healthy fetus.",
    "example_ewe": "Yanuŋkɔkpɔ la fia be ɖevi le dɔme la sesẽ.",
    "category_id": 5,
    "category_name_en": "Medical Procedures"
  },
  {
    "term_en": "Endoscopy",
    "term_ewe": "Lãmekpɔnu",
    "definition_en": "A procedure to examine internal organs using a flexible tube with a camera.",
    "definition_ewe": "Dɔyɔyɔ si tsɔa dɔnu gbadza si ŋu foto le wɔna ŋutilã me kpɔkpɔ.",
    "example_en": "An endoscopy was performed to check her stomach.",
    "example_ewe": "Woaɖe lãmekpɔnu be woakpɔ eƒe fo.",
    "category_id": 5,
    "category_name_en": "Medical Procedures"
  },
  {
    "term_en": "Biopsy",
    "term_ewe": "Lãmeɖeɖe",
    "definition_en": "A procedure to remove a sample of tissue for testing.",
    "definition_ewe": "Dɔyɔyɔ si me wotsɔa lãme ƒe akpa aɖe ɖe be woakpɔ.",
    "example_en": "The biopsy confirmed the diagnosis of cancer.",
    "example_ewe": "Lãmeɖeɖe la kpe ɖe dɔvɔ̃kpɔkpɔ ŋu.",
    "category_id": 5,
    "category_name_en": "Medical Procedures"
  },
  {
    "term_en": "Defibrillator",
    "term_ewe": "Dzigbɔdɔnu",
    "definition_en": "A device that delivers an electric shock to restore heart rhythm.",
    "definition_ewe": "Dɔyɔnu si tsɔa ʋu sesẽ na dzi be yeadzɔ yonyeme.",
    "example_en": "The defibrillator saved his life during cardiac arrest.",
    "example_ewe": "Dzigbɔdɔnu la dzra eƒe agbe le dzi ƒe gbegblẽ megbe.",
    "category_id": 6,
    "category_name_en": "Medical Equipment"
  },
  {
    "term_en": "Suture",
    "term_ewe": "Abibɔnu",
    "definition_en": "A stitch or thread used to close a wound.",
    "definition_ewe": "Nu si wotsɔna bɔna abi be yeadzɔ.",
    "example_en": "The doctor used sutures to close the cut.",
    "example_ewe": "Dɔyɔla la tsɔ abibɔnu bɔ abi la.",
    "category_id": 6,
    "category_name_en": "Medical Equipment"
  },
  {
    "term_en": "Crutch",
    "term_ewe": "Afɔkpe",
    "definition_en": "A support device used to assist with walking.",
    "definition_ewe": "Dɔyɔnu si kpena afɔzɔzɔ me.",
    "example_en": "He used crutches after breaking his leg.",
    "example_ewe": "Ezã afɔkpe le eƒe afɔ ŋe megbe.",
    "category_id": 6,
    "category_name_en": "Medical Equipment"
  },
  {
    "term_en": "Spleen",
    "term_ewe": "Sisã",
    "definition_en": "An organ that filters blood and supports the immune system.",
    "definition_ewe": "Akpa si sĩa ʋu kple ŋusẽdzikpɔkpɔ kpena.",
    "example_en": "The spleen was enlarged due to an infection.",
    "example_ewe": "Sisã la gã ɖe vɔ̃ aɖe ŋu.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Pancreas",
    "term_ewe": "Dɔmenu",
    "definition_en": "An organ that produces insulin and digestive enzymes.",
    "definition_ewe": "Akpa si wɔa suklidɔati kple nuɖuɖu ƒe dɔnuwo.",
    "example_en": "The pancreas regulates blood sugar levels.",
    "example_ewe": "Dɔmenu la dɔa ʋu me suklidzi.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Cholera",
    "term_ewe": "Tsikudɔ",
    "definition_en": "An infectious disease causing severe diarrhea and dehydration.",
    "definition_ewe": "Dɔvɔ̃ si hena afɔku sesẽ kple tsimeme.",
    "example_en": "Cholera outbreaks require clean water to prevent spread.",
    "example_ewe": "Tsikudɔ ƒe gbagbã hiã tsi dzadzɛ be yeadzɔ.",
    "category_id": 2,
    "category_name_en": "Diseases"
  },
  {
    "term_en": "Rash",
    "term_ewe": "Lãmevɔ",
    "definition_en": "A change in skin color or texture, often due to irritation or allergy.",
    "definition_ewe": "Lãme ƒe dzime ƒe tɔtrɔ si va to kuxia alo aladzi.",
    "example_en": "The rash appeared after using a new soap.",
    "example_ewe": "Lãmevɔ la va esi wozã sabun yeye.",
    "category_id": 3,
    "category_name_en": "Symptoms"
  },
  {
    "term_en": "Antacid",
    "term_ewe": "Dɔmedɔati",
    "definition_en": "A medicine that neutralizes stomach acid.",
    "definition_ewe": "Atike si ɖea fo ƒe asid ɖa.",
    "example_en": "She took an antacid for heartburn.",
    "example_ewe": "Exɔ dɔmedɔati na fo ƒe dzodzo.",
    "category_id": 4,
    "category_name_en": "Medications"
  },
  {
    "term_en": "MRI",
    "term_ewe": "Lãmekpɔfoto",
    "definition_en": "A scan using magnetic fields to produce detailed images of organs.",
    "definition_ewe": "Dɔyɔyɔ si tsɔa magnetiknu wɔa ŋutilã foto tɔxɛ.",
    "example_en": "The MRI revealed a torn ligament.",
    "example_ewe": "Lãmekpɔfoto la fia be kloti aɖe ŋe.",
    "category_id": 5,
    "category_name_en": "Medical Procedures"
  },
  {
    "term_en": "Ventilator",
    "term_ewe": "Gbɔgbɔnu",
    "definition_en": "A machine that assists with breathing by delivering air to the lungs.",
    "definition_ewe": "Dɔyɔnu si kpena gbɔgbɔxexe to ya tsoa dzime.",
    "example_en": "The patient was put on a ventilator in the ICU.",
    "example_ewe": "Wodɔ dɔnɔ la le gbɔgbɔnu dzi le ICU me.",
    "category_id": 6,
    "category_name_en": "Medical Equipment"
  },
  {
    "term_en": "Bladder",
    "term_ewe": "Tsitui",
    "definition_en": "The organ that stores urine before excretion.",
    "definition_ewe": "Akpa si kpea tsi hafi wòaɖe go.",
    "example_en": "A bladder infection caused discomfort.",
    "example_ewe": "Tsitui ƒe dɔvɔ̃ la hena kuxi.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Dengue",
    "term_ewe": "Dzodzodɔ",
    "definition_en": "A viral disease transmitted by mosquitoes, causing fever and joint pain.",
    "definition_ewe": "Dɔvɔ̃ si yitiwo kakana, hena dzodzo kple kloti vevesese.",
    "example_en": "Dengue fever is common in tropical areas.",
    "example_ewe": "Dzodzodɔ la zɔna le anyigba siwo le dzodzo me.",
    "category_id": 2,
    "category_name_en": "Diseases"
  },
  {
    "term_en": "Itching",
    "term_ewe": "Lãmeka",
    "definition_en": "An uncomfortable sensation on the skin prompting scratching.",
    "definition_ewe": "Kuxi le lãme dzi si nana ame ka.",
    "example_en": "The itching was caused by an allergic reaction.",
    "example_ewe": "Lãmeka la va to aladzi ŋu.",
    "category_id": 3,
    "category_name_en": "Symptoms"
  },
  {
    "term_en": "Antidepressant",
    "term_ewe": "Dziɖiɖidɔati",
    "definition_en": "A drug used to treat depression and mood disorders.",
    "definition_ewe": "Atike si wotsɔna dzea dziɖiɖi kple susu gbegblẽwo.",
    "example_en": "She was prescribed an antidepressant for her condition.",
    "example_ewe": "Wofia dziɖiɖidɔati na eƒe nɔnɔme.",
    "category_id": 4,
    "category_name_en": "Medications"
  },
  {
    "term_en": "Catheter",
    "term_ewe": "Tsitɔnu",
    "definition_en": "A tube used to drain or deliver fluids in medical procedures.",
    "definition_ewe": "Dɔyɔnu si wotsɔna ɖea tsi alo nana tsi le dɔyɔyɔ me.",
    "example_en": "A catheter was inserted to drain urine.",
    "example_ewe": "Wodɔ tsitɔnu be tsi aɖe go.",
    "category_id": 6,
    "category_name_en": "Medical Equipment"
  },
  {
    "term_en": "Bone",
    "term_ewe": "ƒu",
    "definition_en": "The hard, rigid tissue forming the skeleton.",
    "definition_ewe": "Akpa sesẽ aɖe le wò ŋutilã me si naa wò ŋutilã nɔa nɔnɔme me eye wòkpɔa ŋutinuwo ta .",
    "example_en": "The X-ray showed a fractured bone.",
    "example_ewe": "Lãmekpɔfoto la fia be ƒu ŋe.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Muscle",
    "term_ewe": "Atsu",
    "definition_en": "Tissue that contracts to produce movement.",
    "definition_ewe": "Lãme si kpea be yeadzɔ mɔzɔzɔ.",
    "example_en": "He pulled a muscle while running.",
    "example_ewe": "Eɖe atsu le mɔzɔzɔ me.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
  {
    "term_en": "Skin",
    "term_ewe": "Lãme",
    "definition_en": "The outer covering of the body.",
    "definition_ewe": "Ŋutilã ƒe akpa si kpea dzime.",
    "example_en": "Her skin was burned by the sun.",
    "example_ewe": "Eƒe lãme gblẽ le ɣe ŋu.",
    "category_id": 1,
    "category_name_en": "Body Parts"
  },
])

def add_new_terms():
    with app.app_context():
        added = 0
        for term in NEW_TERMS:
            # Find the category by English name
            category = Category.query.filter_by(name_en=term["category_name_en"]).first()
            if not category:
                print(f"Category '{term['category_name_en']}' not found. Skipping term '{term['term_en']}'.")
                continue
            # Check if term already exists (by English term and category)
            exists = Term.query.filter_by(term_en=term["term_en"], category_id=category.id).first()
            if exists:
                print(f"Term '{term['term_en']}' already exists in category '{term['category_name_en']}'. Skipping.")
                continue
            # Add new term
            new_term = Term(
                term_en=term["term_en"],
                term_ewe=term["term_ewe"],
                definition_en=term["definition_en"],
                definition_ewe=term["definition_ewe"],
                example_en=term.get("example_en"),
                example_ewe=term.get("example_ewe"),
                pronunciation=term.get("pronunciation"),
                category_id=category.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_term)
            added += 1
        db.session.commit()
        print(f"Added {added} new terms.")

# --- Correction for 'Bone' definition_ewe ---
def update_bone_definition():
    with app.app_context():
        bone = Term.query.filter_by(term_en="Bone").first()
        if bone:
            bone.definition_ewe = "Akpa sesẽ aɖe le wò ŋutilã me si naa wò ŋutilã nɔa nɔnɔme me eye wòkpɔa ŋutinuwo ta ."
            bone.updated_at = datetime.utcnow()
            db.session.commit()
            print("Updated Ewe definition for 'Bone'.")
        else:
            print("'Bone' term not found in the database.")

# --- Correction for 'Bone' term_ewe ---
def update_bone_term_ewe():
    with app.app_context():
        bone = Term.query.filter_by(term_en="Bone").first()
        if bone:
            bone.term_ewe = "ƒu"
            bone.updated_at = datetime.utcnow()
            db.session.commit()
            print("Updated Ewe term for 'Bone' to 'ƒu'.")
        else:
            print("'Bone' term not found in the database.")

if __name__ == "__main__":
    add_new_terms()
    update_bone_definition()
    update_bone_term_ewe()
