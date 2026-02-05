from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from pydantic_ai import Agent

dict_of_level = {
    "WORKS": "Works",
    "GOODS": "Goods",
    "SERVICES": "Services",
    "OTHER": "Other",
    "W01": "Барилга байгууламж",
    "W02": "Зам, гүүр",
    "W03": "Инженерийн дэд бүтэц",
    "W04": "Их засвар, шинэчлэл",
    "W05": "EPC / Design-Build",
    "W06": "Бусад барилгын ажил",
    "G01": "IT тоног төхөөрөмж",
    "G02": "Тээврийн хэрэгсэл",
    "G03": "Эмнэлгийн бараа",
    "G04": "Оффисын бараа",
    "G05": "Түлш, эрчим хүч",
    "G06": "Барилгын материал, сэлбэг",
    "G07": "Хүнс, өргөн хэрэглээний бараа",
    "G08": "Өргөн хэрэглээний бүтээгдэхүүн",
    "G09": "Хувцас, хамгаалах хэрэгсэл",
    "G10": "Боловсролын материал",
    "G11": "Хөдөө аж ахуйн бүтээгдэхүүн",
    "G12": "Хэвлэлийн бүтээгдэхүүн",
    "G13": "Гал тогоо, хоол үйлдвэрлэлийн тоног төхөөрөмж",
    "G14": "Аюулгүй байдал, хяналтын төхөөрөмж",
    "G15": "Лаборатори, шинжилгээний хэрэгсэл, урвалж",
    "G16": "Соёл, спорт, арга хэмжээний тоног төхөөрөмж",
    "S01": "Цэвэрлэгээ",
    "S02": "Хамгаалалт",
    "S03": "Тээвэр, ложистик",
    "S04": "Засвар үйлчилгээ",
    "S05": "Даатгал",
    "S06": "Outsourcing",
    "S07": "Шуудан, курьер, хүргэлтийн үйлчилгээ",
    "S08": "Харилцаа холбооны үйлчилгээ",
    "S09": "Сургалт, чадавх бэхжүүлэх үйлчилгээ",
    "S10": "Програм хангамж",
    "S11": "ERP / HRMS",
    "S12": "E-Government",
    "S13": "Өгөгдөл, дата",
    "S14": "Кибер аюулгүй байдал",
    "S15": "Cloud / Hosting",
    "S16": "IT Support",
    "S17": "Орчуулга, хэлмэрчийн үйлчилгээ",
    "S18": "Судалгаа, санал асуулга, мэдээлэл цуглуулалт",
    "S19": "Барилга, байгууламжийн ашиглалт, арчлалт",
    "S20": "ТЭЗҮ",
    "S21": "Судалгаа",
    "S22": "Бодлогын зөвлөх",
    "S23": "Аудит",
    "S24": "Төслийн менежмент",
    "S25": "Зураг төсөл",
    "S26": "Хэвлэлийн үйлчилгээ",
    "S27": "Хоол үйлдвэрлэл, кейтеринг",
    "S28": "Хог хаягдлын менежмент",
    "S29": "Ашиглалтын үйлчилгээ (ус, дулаан, цахилгаан)",
    "S30": "Харилцаа холбоо, медиа үйлчилгээ",
    "S31": "Арга хэмжээ зохион байгуулалт",
    "S32": "Түрээс, лизинг",
    "S33": "Геологи, уул уурхайн үйлчилгээ",
    "S34": "Хууль, эрх зүйн үйлчилгээ",
    "W01_001": "Орон сууц",
    "W01_002": "Захиргааны барилга",
    "W01_003": "Сургууль",
    "W01_004": "Цэцэрлэг",
    "W01_005": "Эмнэлэг",
    "W01_006": "Соёлын төв",
    "W01_007": "Спорт заал",
    "W01_008": "Агуулах",
    "W01_009": "Үйлдвэрийн барилга",
    "W02_001": "Авто зам",
    "W02_002": "Гүүр",
    "W02_003": "Туннель",
    "W02_004": "Замын байгууламж",
    "W02_005": "Явган зам",
    "W03_001": "Цахилгаан",
    "W03_002": "Дулаан",
    "W03_003": "Ус хангамж",
    "W03_004": "Бохир ус",
    "W03_005": "Харилцаа холбоо",
    "W04_001": "Барилгын их засвар",
    "W04_002": "Замын их засвар",
    "W04_003": "Дэд бүтцийн засвар",
    "W05_001": "EPC гэрээ",
    "W05_002": "Design-Build гэрээ",
    "W06_001": "Ландшафт",
    "W06_002": "Тохижилт",
    "W06_003": "Гадна талбай",
    "G01_001": "Суурин компьютер",
    "G01_002": "Зөөврийн компьютер",
    "G01_003": "Сервер",
    "G01_004": "Сүлжээний төхөөрөмж",
    "G01_005": "Хадгалах төхөөрөмж",
    "G01_006": "Принтер",
    "G02_001": "Суудлын автомашин",
    "G02_002": "Ачааны автомашин",
    "G02_003": "Тусгай зориулалтын машин",
    "G02_004": "Автобус",
    "G02_005": "Мотоцикл",
    "G03_001": "Эмнэлгийн тоног төхөөрөмж",
    "G03_002": "Оношилгооны төхөөрөмж",
    "G03_003": "Эм",
    "G03_004": "Вакцин",
    "G03_005": "Эмнэлгийн хэрэгсэл",
    "G04_001": "Тавилга",
    "G04_002": "Тоноглол",
    "G04_003": "Бичиг хэрэг",
    "G04_004": "Цаас",
    "G04_005": "Хэвлэлийн хор",
    "G05_001": "Шатахуун",
    "G05_002": "Нүүрс",
    "G05_003": "Түлээ",
    "G05_004": "Цахилгаан эрчим хүч",
    "G05_005": "Газ",
    "G06_001": "Барилгын материал",
    "G06_002": "Сэлбэг хэрэгсэл",
    "G06_003": "Химийн бодис",
    "G07_001": "Будаа",
    "G07_002": "Гурил",
    "G07_003": "Талх",
    "G07_004": "Мах",
    "G07_005": "Сүү, сүүн бүтээгдэхүүн",
    "G07_006": "Жимс",
    "G07_007": "Хүнсний ногоо",
    "G07_008": "Лаазалсан хүнс",
    "G07_009": "Ундаа, ус",
    "G08_001": "Ахуйн цэвэрлэгээний бодис",
    "G08_002": "Ариун цэврийн цаас",
    "G08_003": "Саван, угаалгын бодис",
    "G08_004": "Ариутгалын хэрэгсэл",
    "G08_005": "Нэг удаагийн хэрэглээний бүтээгдэхүүн",
    "G09_001": "Ажлын хувцас",
    "G09_002": "Дүрэмт хувцас",
    "G09_003": "ХАБЭА хэрэгсэл",
    "G09_004": "Гутал",
    "G09_005": "Бээлий",
    "G10_001": "Сурах бичиг",
    "G10_002": "Ном",
    "G10_003": "Сургалтын хэрэглэгдэхүүн",
    "G10_004": "Лабораторийн хэрэгсэл",
    "G11_001": "Үр, тариалалтын үр",
    "G11_002": "Бордоо",
    "G11_003": "Малын тэжээл",
    "G11_004": "Мал эмнэлгийн эм",
    "G11_005": "Малын вакцин",
    "G11_006": "ХАА-н химийн бодис",
    "G12_001": "Маягт, бланк",
    "G12_002": "Сертификат, үнэмлэх",
    "G12_003": "Сонгуулийн материал",
    "G12_004": "Ном, гарын авлага",
    "G12_005": "Сурталчилгааны хэвлэл",
    "G13_001": "Аж үйлдвэрийн плитка, зуух",
    "G13_002": "Хөргөгч, хөлдөөгч",
    "G13_003": "Аяга таваг угаагч, угаалгын төхөөрөмж",
    "G13_004": "Хоол боловсруулах машин, миксер, хэрчигч",
    "G13_005": "Сав суулга, тавиур, тоноглол",
    "G13_006": "Сургуулийн гал тогооны иж бүрдэл",
    "G14_001": "Хяналтын камер (CCTV)",
    "G14_002": "Нэвтрэх хяналт (access control)",
    "G14_003": "Дохиоллын систем",
    "G14_004": "Галын дохиолол, мэдрэгч",
    "G14_005": "Металл илрүүлэгч, шалгах төхөөрөмж",
    "G15_001": "Лабораторийн тоног төхөөрөмж",
    "G15_002": "Шинжилгээний урвалж, химийн бодис",
    "G15_003": "Сорьц авах хэрэгсэл",
    "G15_004": "Лабораторийн нэг удаагийн хэрэгсэл",
    "G15_005": "Калибрац, стандарт материал",
    "G16_001": "Спортын тоног төхөөрөмж",
    "G16_002": "Дуу, дүрсний төхөөрөмж",
    "G16_003": "Тайз, гэрэлтүүлэг, акустик тоноглол",
    "G16_004": "Номын сангийн тоноглол",
    "G16_005": "Сургалтын лаборатори/STEAM тоноглол",
    "S01_001": "Барилга",
    "S01_002": "Гадна талбай",
    "S01_003": "Цонх угаалга",
    "S02_001": "Харуул",
    "S02_002": "Дохиолол",
    "S02_003": "Камер хяналт",
    "S03_001": "Ачаа тээвэр",
    "S03_002": "Зорчигч тээвэр",
    "S03_003": "Агуулах",
    "S04_001": "Барилга",
    "S04_002": "Тоног төхөөрөмж",
    "S04_003": "Тээврийн хэрэгсэл",
    "S05_001": "Эрүүл мэнд",
    "S05_002": "Эд хөрөнгө",
    "S05_003": "Авто тээвэр",
    "S06_001": "IT аутсорсинг",
    "S06_002": "Нягтлан бодох",
    "S06_003": "HR үйлчилгээ",
    "S07_001": "Шуудангийн үйлчилгээ",
    "S07_002": "Курьер үйлчилгээ",
    "S07_003": "Албан бичиг, илгээмж тээвэрлэлт",
    "S07_004": "Шуурхай хүргэлт (express)",
    "S07_005": "Дотоод/гадаад илгээмжийн үйлчилгээ",
    "S08_001": "Суурин холбооны үйлчилгээ",
    "S08_002": "Гар утасны үйлчилгээ (SIM/дугаар/багц)",
    "S08_003": "Дата холбоо, VPN үйлчилгээ",
    "S08_004": "Интернэт үйлчилгээ",
    "S08_005": "IP телефони, call center шугам",
    "S09_001": "Мэргэжлийн сургалт",
    "S09_002": "IT сургалт",
    "S09_003": "ХАБЭА сургалт",
    "S09_004": "Удирдлага, манлайллын сургалт",
    "S09_005": "Сургалтын материал боловсруулах",
    "S10_001": "Захиалгат хөгжүүлэлт",
    "S10_002": "Систем шинэчлэл",
    "S10_003": "Лиценз нийлүүлэлт",
    "S11_001": "ERP нэвтрүүлэлт",
    "S11_002": "HRMS",
    "S11_003": "Санхүүгийн систем",
    "S11_004": "Нягтлан бодох систем",
    "S12_001": "Төрийн портал",
    "S12_002": "Цахим үйлчилгээ",
    "S12_003": "Интеграци",
    "S13_001": "Регистрийн систем",
    "S13_002": "Дата агуулах",
    "S13_003": "BI систем",
    "S14_001": "Security audit",
    "S14_002": "SOC үйлчилгээ",
    "S14_003": "Penetration test",
    "S15_001": "Cloud үйлчилгээ",
    "S15_002": "Дата төв",
    "S15_003": "Backup үйлчилгээ",
    "S16_001": "SLA дэмжлэг",
    "S16_002": "Helpdesk",
    "S16_003": "System monitoring",
    "S17_001": "Бичгийн орчуулга",
    "S17_002": "Албан баримт бичгийн орчуулга",
    "S17_003": "Амнаас ам дамжсан орчуулга",
    "S17_004": "Синхрон орчуулга",
    "S17_005": "Хэлмэрчийн үйлчилгээ",
    "S18_001": "Санал асуулга зохион байгуулалт",
    "S18_002": "Талбарын судалгаа",
    "S18_003": "Мэдээлэл цуглуулалт",
    "S18_004": "Дата оруулах, кодлох",
    "S18_005": "Тайлан бэлтгэх (execution)",
    "S19_001": "Барилга ашиглалтын үйлчилгээ",
    "S19_002": "Цахилгаан, сантехникийн арчлалт",
    "S19_003": "Лифт, тоног төхөөрөмжийн арчилгаа",
    "S19_004": "Ногоон байгууламжийн арчилгаа",
    "S19_005": "Facility management үйлчилгээ",
    "S20_001": "Feasibility study",
    "S20_002": "Cost-benefit analysis",
    "S21_001": "Судалгаа шинжилгээ",
    "S21_002": "Үнэлгээ",
    "S22_001": "Policy advisory",
    "S22_002": "Strategy consulting",
    "S23_001": "Санхүүгийн аудит",
    "S23_002": "IT аудит",
    "S24_001": "PMO",
    "S24_002": "Төслийн хяналт",
    "S25_001": "Архитектур",
    "S25_002": "Инженерийн зураг төсөл",
    "S26_001": "Хэвлэх үйлчилгээ",
    "S26_002": "Хуулбарлах үйлчилгээ",
    "S26_003": "Дизайн, эх бэлтгэл",
    "S26_004": "Биндэрлэх, хавтаслах",
    "S27_001": "Сургуулийн хоол үйлдвэрлэл",
    "S27_002": "Эмнэлгийн хоол үйлдвэрлэл",
    "S27_003": "Кейтеринг үйлчилгээ",
    "S27_004": "Гал тогооны үйлчилгээний аутсорсинг",
    "S28_001": "Хог тээвэрлэлт",
    "S28_002": "Хог ангилан ялгалт",
    "S28_003": "Хог булшлах/устгах",
    "S28_004": "Дахин боловсруулах үйлчилгээ",
    "S28_005": "Аюултай хог хаягдал",
    "S29_001": "Ус хангамжийн үйлчилгээ",
    "S29_002": "Дулааны үйлчилгээ",
    "S29_003": "Цахилгаан хангамжийн үйлчилгээ",
    "S29_004": "Суурин холбоо/интернэт үйлчилгээ",
    "S30_001": "Медиа төлөвлөлт, худалдан авалт",
    "S30_002": "Контент үйлдвэрлэл",
    "S30_003": "PR үйлчилгээ",
    "S30_004": "Зар сурталчилгааны үйлчилгээ",
    "S31_001": "Хурал, форум зохион байгуулалт",
    "S31_002": "Тайз, тоноглол түрээс",
    "S31_003": "Орчуулга, синхрон орчуулга",
    "S31_004": "Байршил, логистикийн зохион байгуулалт",
    "S32_001": "Тээврийн хэрэгслийн түрээс",
    "S32_002": "Тоног төхөөрөмжийн түрээс",
    "S32_003": "Оффис, талбай түрээс",
    "S32_004": "Лизинг үйлчилгээ",
    "S33_001": "Геологийн судалгаа",
    "S33_002": "Өрөмдлөгийн үйлчилгээ",
    "S33_003": "Лабораторийн шинжилгээ",
    "S33_004": "Уул уурхайн зөвлөх үйлчилгээ",
    "S34_001": "Хууль зүйн зөвлөгөө",
    "S34_002": "Гэрээ, баримт бичиг боловсруулах",
    "S34_003": "Шүүхийн төлөөлөл",
    "S34_004": "Арбитрын үйлчилгээ",
}

class TenderType(str, Enum):
    """Top-level tender buckets used to pick Goods, Services, Works, or Other."""
    GOODS = "GOODS"
    SERVICES = "SERVICES"
    WORKS = "WORKS"
    OTHER = "OTHER"

    @property
    def description(self) -> str:
        descriptions = {
            self.GOODS: "Goods => Tangible movable property that is procured, supplied or delivered (e.g., equipment, materials, consumables).",
            self.SERVICES: "Services => Intangible activities in which the main output is labor, expertise or know‑how, rather than a physical product (e.g., consulting, maintenance, training).",
            self.WORKS: "Works => Construction or civil engineering operations resulting in, or substantially modifying, an immovable built asset (e.g., buildings, roads, infrastructure).",
            self.OTHER: "Other => Procurements that do not clearly or predominantly fall under Goods, Services or Works; use only as a last‑resort classification.",
        }
        return descriptions.get(self, "No description available")

class TenderCategory(str, Enum):
    """Level-2 functional procurement categories grouped under the main tender types (Works, Goods, Services, Other)."""
    #W-6 level codes
    W01 = "W01"
    W02 = "W02"
    W03 = "W03"
    W04 = "W04"
    W05 = "W05"
    W06 = "W06"
    #G-16 level codes (Goods)
    G01 = "G01"
    G02 = "G02"
    G03 = "G03"
    G04 = "G04"
    G05 = "G05"
    G06 = "G06"
    G07 = "G07"
    G08 = "G08"
    G09 = "G09"
    G10 = "G10"
    G11 = "G11"
    G12 = "G12"
    G13 = "G13"
    G14 = "G14"
    G15 = "G15"
    G16 = "G16"
    #S-34 (Services)
    S01 = "S01"
    S02 = "S02"
    S03 = "S03"
    S04 = "S04"
    S05 = "S05"
    S06 = "S06"
    S07 = "S07"
    S08 = "S08"
    S09 = "S09"
    S10 = "S10"
    S11 = "S11"
    S12 = "S12"
    S13 = "S13"
    S14 = "S14"
    S15 = "S15"
    S16 = "S16"
    S17 = "S17"
    S18 = "S18"
    S19 = "S19"
    S20 = "S20"
    S21 = "S21"
    S22 = "S22"
    S23 = "S23"
    S24 = "S24"
    S25 = "S25"
    S26 = "S26"
    S27 = "S27"
    S28 = "S28"
    S29 = "S29"
    S30 = "S30"
    S31 = "S31"
    S32 = "S32"
    S33 = "S33"
    S34 = "S34"
    Other = "Other"

    #here should be descriptions for each code
    @property
    def description(self) -> str:
        descriptions = {
            # Works descriptions (строительство / барилга)
            self.W01: "Барилга байгууламж => Building construction (schools, hospitals, offices, factories).",
            self.W02: "Зам, гүүр => Road and bridge construction (roads, bridges, tunnels).",
            self.W03: "Инженерийн дэд бүтэц => Utility infrastructure (power, water, heating, telecom).",
            self.W04: "Их засвар, шинэчлэл => Major repair and renovation of existing assets.",
            self.W05: "EPC / Design-Build => Turnkey design-and-build construction contracts (EPC, DB).",
            self.W06: "Бусад барилгын ажил => Other construction works not covered by W01–W05.",
            # Goods descriptions (бараа)
            self.G01: "IT тоног төхөөрөмж => IT hardware (computers, servers, network devices, printers).",
            self.G02: "Тээврийн хэрэгсэл => Vehicles for passenger or goods transport, including special vehicles.",
            self.G03: "Эмнэлгийн бараа => Medical equipment, medicines and medical consumables.",
            self.G04: "Оффисын бараа => Office furniture, equipment and supplies (stationery, paper, toner).",
            self.G05: "Түлш, эрчим хүч => Fuels and energy (petrol, diesel, coal, gas, electricity).",
            self.G06: "Барилгын материал, сэлбэг => Construction materials and spare parts.",
            self.G07: "Хүнс, өргөн хэрэглээний бараа => Food and basic consumer goods (rice, flour, bread, meat, dairy, fruit, vegetables, canned food, drinks).",
            self.G08: "Өргөн хэрэглээний бүтээгдэхүүн => Non‑food household and hygiene products (soap, detergent, cleaning items).",
            self.G09: "Хувцас, хамгаалах хэрэгсэл => Clothing, uniforms and personal protective equipment.",
            self.G10: "Боловсролын материал => Educational books, lab sets and teaching materials.",
            self.G11: "Хөдөө аж ахуйн бүтээгдэхүүн => Agricultural inputs (seed, fertilizer, feed, veterinary items).",
            self.G12: "Хэвлэлийн бүтээгдэхүүн => Printed products (forms, certificates, election and promo print).",
            self.G13: "Гал тогоо, хоол үйлдвэрлэлийн тоног төхөөрөмж => Kitchen and catering equipment.",
            self.G14: "Аюулгүй байдал, хяналтын төхөөрөмж => Security and surveillance equipment.",
            self.G15: "Лаборатори, шинжилгээний хэрэгсэл, урвалж => Laboratory equipment, reagents and consumables.",
            self.G16: "Соёл, спорт, арга хэмжээний тоног төхөөрөмж => Cultural, sports and event equipment.",
            # Services descriptions (үйлчилгээ)
            self.S01: "Цэвэрлэгээ => Cleaning services for buildings and outdoor areas.",
            self.S02: "Хамгаалалт => Guarding, alarm monitoring and CCTV security services.",
            self.S03: "Тээвэр, ложистик => Passenger and freight transport, warehousing and logistics.",
            self.S04: "Засвар үйлчилгээ => Maintenance and repair for buildings, equipment and vehicles.",
            self.S05: "Даатгал => Insurance services for people, property and vehicles.",
            self.S06: "Outsourcing => Outsourced business services (IT, accounting, HR).",
            self.S07: "Шуудан, курьер, хүргэлтийн үйлчилгээ => Postal, courier and delivery services.",
            self.S08: "Харилцаа холбооны үйлчилгээ => Telecom services (mobile, fixed, internet, data).",
            self.S09: "Сургалт, чадавх бэхжүүлэх үйлчилгээ => Training and capacity‑building services.",
            self.S10: "Програм хангамж => Software development, customization and licensing.",
            self.S11: "ERP / HRMS => ERP, HR and related enterprise‑system services.",
            self.S12: "E-Government => E‑government portals and digital public services.",
            self.S13: "Өгөгдөл, дата => Data platforms, BI and registry systems.",
            self.S14: "Кибер аюулгүй байдал => Cyber‑security, SOC and penetration‑testing services.",
            self.S15: "Cloud / Hosting => Cloud, hosting, data‑center and backup services.",
            self.S16: "IT Support => IT support, helpdesk and system‑monitoring services.",
            self.S17: "Орчуулга, хэлмэрчийн үйлчилгээ => Translation and interpretation services.",
            self.S18: "Судалгаа, санал асуулга, мэдээлэл цуглуулалт => Surveys, research and data‑collection services.",
            self.S19: "Барилга, байгууламжийн ашиглалт, арчлалт => Facility operation and building maintenance services.",
            self.S20: "ТЭЗҮ => Feasibility and economic/financial study services.",
            self.S21: "Судалгаа => Policy, program or sector research and evaluation.",
            self.S22: "Бодлогын зөвлөх => Policy and strategy consulting services.",
            self.S23: "Аудит => Financial and IT audit services.",
            self.S24: "Төслийн менежмент => Project‑management and PMO support services.",
            self.S25: "Зураг төсөл => Architectural and engineering design services.",
            self.S26: "Хэвлэлийн үйлчилгээ => Printing, copying and pre‑press services.",
            self.S27: "Хоол үйлдвэрлэл, кейтеринг => Catering and institutional food‑service provision.",
            self.S28: "Хог хаягдлын менежмент => Waste collection, treatment and disposal services.",
            self.S29: "Ашиглалтын үйлчилгээ (ус, дулаан, цахилгаан) => Operation of utilities (water, heat, electricity, communications).",
            self.S30: "Харилцаа холбоо, медиа үйлчилгээ => Media, communication and advertising services.",
            self.S31: "Арга хэмжээ зохион байгуулалт => Event organization and related logistics.",
            self.S32: "Түрээс, лизинг => Rental and leasing of vehicles, equipment and premises.",
            self.S33: "Геологи, уул уурхайн үйлчилгээ => Geological, drilling, laboratory and mining consulting.",
            self.S34: "Хууль, эрх зүйн үйлчилгээ => Legal advice, contracts and representation services.",
            self.Other: "Other items not covered above",
        }
        return descriptions.get(self, "No description available")

class TenderCategoryItem(str, Enum):
    """Level-3 detail codes that refine a main category into a specific item."""
    # Works level three codes
    W01_001 = "W01_001"
    W01_002 = "W01_002"
    W01_003 = "W01_003"
    W01_004 = "W01_004"
    W01_005 = "W01_005"
    W01_006 = "W01_006"
    W01_007 = "W01_007"
    W01_008 = "W01_008"
    W01_009 = "W01_009"
    W02_001 = "W02_001"
    W02_002 = "W02_002"
    W02_003 = "W02_003"
    W02_004 = "W02_004"
    W02_005 = "W02_005"
    W03_001 = "W03_001"
    W03_002 = "W03_002"
    W03_003 = "W03_003"
    W03_004 = "W03_004"
    W03_005 = "W03_005"
    W04_001 = "W04_001"
    W04_002 = "W04_002"
    W04_003 = "W04_003"
    W05_001 = "W05_001"
    W05_002 = "W05_002"
    W06_001 = "W06_001"
    W06_002 = "W06_002"
    W06_003 = "W06_003"
    # Goods level three codes
    G01_001 = "G01_001"
    G01_002 = "G01_002"
    G01_003 = "G01_003"
    G01_004 = "G01_004"
    G01_005 = "G01_005"
    G01_006 = "G01_006"
    G02_001 = "G02_001"
    G02_002 = "G02_002"
    G02_003 = "G02_003"
    G02_004 = "G02_004"
    G02_005 = "G02_005"
    G03_001 = "G03_001"
    G03_002 = "G03_002"
    G03_003 = "G03_003"
    G03_004 = "G03_004"
    G03_005 = "G03_005"
    G04_001 = "G04_001"
    G04_002 = "G04_002"
    G04_003 = "G04_003"
    G04_004 = "G04_004"
    G04_005 = "G04_005"
    G05_001 = "G05_001"
    G05_002 = "G05_002"
    G05_003 = "G05_003"
    G05_004 = "G05_004"
    G05_005 = "G05_005"
    G06_001 = "G06_001"
    G06_002 = "G06_002"
    G06_003 = "G06_003"
    G07_001 = "G07_001"
    G07_002 = "G07_002"
    G07_003 = "G07_003"
    G07_004 = "G07_004"
    G07_005 = "G07_005"
    G07_006 = "G07_006"
    G07_007 = "G07_007"
    G07_008 = "G07_008"
    G07_009 = "G07_009"
    G08_001 = "G08_001"
    G08_002 = "G08_002"
    G08_003 = "G08_003"
    G08_004 = "G08_004"
    G08_005 = "G08_005"
    G09_001 = "G09_001"
    G09_002 = "G09_002"
    G09_003 = "G09_003"
    G09_004 = "G09_004"
    G09_005 = "G09_005"
    G10_001 = "G10_001"
    G10_002 = "G10_002"
    G10_003 = "G10_003"
    G10_004 = "G10_004"
    G11_001 = "G11_001"
    G11_002 = "G11_002"
    G11_003 = "G11_003"
    G11_004 = "G11_004"
    G11_005 = "G11_005"
    G11_006 = "G11_006"
    G12_001 = "G12_001"
    G12_002 = "G12_002"     
    G12_003 = "G12_003"
    G12_004 = "G12_004"
    G12_005 = "G12_005"
    G13_001 = "G13_001"
    G13_002 = "G13_002"
    G13_003 = "G13_003"
    G13_004 = "G13_004"
    G13_005 = "G13_005"
    G13_006 = "G13_006"
    G14_001 = "G14_001"
    G14_002 = "G14_002"
    G14_003 = "G14_003"
    G14_004 = "G14_004"
    G14_005 = "G14_005"
    G15_001 = "G15_001"
    G15_002 = "G15_002"
    G15_003 = "G15_003"
    G15_004 = "G15_004"
    G15_005 = "G15_005"
    G16_001 = "G16_001"
    G16_002 = "G16_002"
    G16_003 = "G16_003"
    G16_004 = "G16_004"
    G16_005 = "G16_005"

    # Services level three codes
    S01_001 = "S01_001"
    S01_002 = "S01_002"
    S01_003 = "S01_003"
    S02_001 = "S02_001"
    S02_002 = "S02_002"
    S02_003 = "S02_003"
    S03_001 = "S03_001"
    S03_002 = "S03_002"
    S03_003 = "S03_003"
    S04_001 = "S04_001"
    S04_002 = "S04_002"
    S04_003 = "S04_003"
    S05_001 = "S05_001"
    S05_002 = "S05_002"
    S05_003 = "S05_003"
    S06_001 = "S06_001"
    S06_002 = "S06_002"
    S06_003 = "S06_003"
    S07_001 = "S07_001"
    S07_002 = "S07_002"
    S07_003 = "S07_003"
    S07_004 = "S07_004"
    S07_005 = "S07_005"
    S08_001 = "S08_001"
    S08_002 = "S08_002"
    S08_003 = "S08_003"
    S08_004 = "S08_004"
    S08_005 = "S08_005"
    S09_001 = "S09_001"
    S09_002 = "S09_002"
    S09_003 = "S09_003"
    S09_004 = "S09_004"
    S09_005 = "S09_005"
    S10_001 = "S10_001"
    S10_002 = "S10_002"
    S10_003 = "S10_003"
    S11_001 = "S11_001"
    S11_002 = "S11_002"
    S11_003 = "S11_003"
    S11_004 = "S11_004"
    S12_001 = "S12_001"
    S12_002 = "S12_002"
    S12_003 = "S12_003"
    S13_001 = "S13_001"
    S13_002 = "S13_002"
    S13_003 = "S13_003"
    S14_001 = "S14_001"
    S14_002 = "S14_002"
    S14_003 = "S14_003"
    S15_001 = "S15_001"
    S15_002 = "S15_002"
    S15_003 = "S15_003"
    S16_001 = "S16_001"
    S16_002 = "S16_002"
    S16_003 = "S16_003"
    S17_001 = "S17_001"
    S17_002 = "S17_002"
    S17_003 = "S17_003"
    S17_004 = "S17_004"
    S17_005 = "S17_005"
    S18_001 = "S18_001"
    S18_002 = "S18_002"
    S18_003 = "S18_003"
    S18_004 = "S18_004"
    S18_005 = "S18_005"
    S19_001 = "S19_001"
    S19_002 = "S19_002"
    S19_003 = "S19_003"
    S19_004 = "S19_004"
    S19_005 = "S19_005"
    S20_001 = "S20_001"
    S20_002 = "S20_002"
    S21_001 = "S21_001"
    S21_002 = "S21_002"
    S22_001 = "S22_001"
    S22_002 = "S22_002"
    S23_001 = "S23_001"
    S23_002 = "S23_002"
    S24_001 = "S24_001"
    S24_002 = "S24_002"
    S25_001 = "S25_001"
    S25_002 = "S25_002"
    S26_001 = "S26_001"
    S26_002 = "S26_002"
    S26_003 = "S26_003"
    S26_004 = "S26_004"
    S27_001 = "S27_001"
    S27_002 = "S27_002"
    S27_003 = "S27_003"
    S27_004 = "S27_004"
    S28_001 = "S28_001"
    S28_002 = "S28_002"
    S28_003 = "S28_003"
    S28_004 = "S28_004"
    S28_005 = "S28_005"
    S29_001 = "S29_001"
    S29_002 = "S29_002"
    S29_003 = "S29_003"
    S29_004 = "S29_004"
    S30_001 = "S30_001"
    S30_002 = "S30_002"
    S30_003 = "S30_003"
    S30_004 = "S30_004"
    S31_001 = "S31_001"
    S31_002 = "S31_002"
    S31_003 = "S31_003"
    S31_004 = "S31_004"
    S32_001 = "S32_001"
    S32_002 = "S32_002"
    S32_003 = "S32_003"
    S32_004 = "S32_004"
    S33_001 = "S33_001"
    S33_002 = "S33_002"
    S33_003 = "S33_003"
    S33_004 = "S33_004"
    S34_001 = "S34_001"
    S34_002 = "S34_002"
    S34_003 = "S34_003"
    S34_004 = "S34_004"
    Other = "Other"

    @property
    def description(self) -> str:
        descriptions = {
            # Works descriptions
            self.W01_001: "Орон сууц => Residential apartment buildings for housing.",
            self.W01_002: "Захиргааны барилга => Administrative and office buildings.",
            self.W01_003: "Сургууль => School and educational buildings.",
            self.W01_004: "Цэцэрлэг => Kindergarten and preschool buildings.",
            self.W01_005: "Эмнэлэг => Hospital and clinic buildings.",
            self.W01_006: "Соёлын төв => Cultural buildings (cultural centers, museums, libraries).",
            self.W01_007: "Спорт заал => Indoor sports halls and gyms.",
            self.W01_008: "Агуулах => Warehouse and logistics storage buildings.",
            self.W01_009: "Үйлдвэрийн барилга => Industrial and production buildings.",

            self.W02_001: "Авто зам => Roads and highways.",
            self.W02_002: "Гүүр => Road and pedestrian bridges.",
            self.W02_003: "Туннель => Tunnels for roads, rail, or utilities.",
            self.W02_004: "Замын байгууламж => Road structures (interchanges, culverts, retaining walls).",
            self.W02_005: "Явган зам => Pedestrian paths and sidewalks.",

            self.W03_001: "Цахилгаан => Electrical infrastructure (lines, substations).",
            self.W03_002: "Дулаан => District heating and boiler infrastructure.",
            self.W03_003: "Ус хангамж => Water supply plants and networks.",
            self.W03_004: "Бохир ус => Wastewater and sewage systems.",
            self.W03_005: "Харилцаа холбоо => Fixed communication networks and related works.",

            self.W04_001: "Барилгын их засвар => Major repair of buildings (capital repair).",
            self.W04_002: "Замын их засвар => Major repair of roads and related structures.",
            self.W04_003: "Дэд бүтцийн засвар => Major repair of utility and infrastructure systems.",

            self.W05_001: "EPC гэрээ => EPC turnkey contract (design, procurement, construction).",
            self.W05_002: "Design-Build гэрээ => Design–Build turnkey contract.",

            self.W06_001: "Ландшафт => Landscaping and green area works.",
            self.W06_002: "Тохижилт => Urban beautification and amenity works.",
            self.W06_003: "Гадна талбай => Outdoor site and yard development works.",

            # Goods descriptions
            self.G01_001: "Суурин компьютер => Desktop computers and workstations.",
            self.G01_002: "Зөөврийн компьютер => Laptop and notebook computers.",
            self.G01_003: "Сервер => Server hardware for data centers.",
            self.G01_004: "Сүлжээний төхөөрөмж => Network equipment (switch, router, firewall, access point).",
            self.G01_005: "Хадгалах төхөөрөмж => Data storage devices (NAS, SAN, backup).",
            self.G01_006: "Принтер => Printers and similar printing devices.",

            self.G02_001: "Суудлын автомашин => Passenger cars and SUVs.",
            self.G02_002: "Ачааны автомашин => Cargo and dump trucks.",
            self.G02_003: "Тусгай зориулалтын машин => Special-purpose vehicles (fire truck, ambulance, crane, mixer).",
            self.G02_004: "Автобус => Buses and minibuses for passengers.",
            self.G02_005: "Мотоцикл => Motorcycles and scooters.",

            self.G03_001: "Эмнэлгийн тоног төхөөрөмж => Medical equipment (diagnostic, imaging, surgical, monitoring).",
            self.G03_002: "Оношилгооны төхөөрөмж => Diagnostic devices and laboratory analyzers.",
            self.G03_003: "Эм => Human medicines and pharmaceutical products.",
            self.G03_004: "Вакцин => Human vaccines for immunization.",
            self.G03_005: "Эмнэлгийн хэрэгсэл => Medical consumables and instruments (syringes, gauze, catheters, etc.).",

            self.G04_001: "Тавилга => Office and institutional furniture (desks, chairs, cabinets).",
            self.G04_002: "Тоноглол => Office equipment (copier, shredder, projector, POS, kiosk).",
            self.G04_003: "Бичиг хэрэг => Stationery and office supplies (pens, files, notebooks, etc.).",
            self.G04_004: "Цаас => Paper products (office paper, receipt rolls, special paper).",
            self.G04_005: "Хэвлэлийн хор => Printing consumables (toner, ink cartridges, ribbons).",

            self.G05_001: "Шатахуун => Liquid fuels (gasoline, diesel, aviation fuel).",
            self.G05_002: "Нүүрс => Coal for heating or power.",
            self.G05_003: "Түлээ => Firewood and biomass fuels for heating.",
            self.G05_004: "Цахилгаан эрчим хүч => Electricity as an energy commodity.",
            self.G05_005: "Газ => Gaseous fuels (LPG, natural gas).",

            self.G06_001: "Барилгын материал => Construction materials (cement, steel, bricks, aggregates, etc.).",
            self.G06_002: "Сэлбэг хэрэгсэл => Spare parts for equipment, vehicles, and plant.",
            self.G06_003: "Химийн бодис => Chemical products for construction, industry, or labs.",

            self.G07_001: "Будаа => Rice for food consumption.",
            self.G07_002: "Гурил => Flour and flour mixes for food.",
            self.G07_003: "Талх => Bread and basic bakery products.",
            self.G07_004: "Мах => Fresh or frozen meat products.",
            self.G07_005: "Сүү, сүүн бүтээгдэхүүн => Milk and dairy products (milk, yogurt, cheese).",
            self.G07_006: "Жимс => Fresh fruit.",
            self.G07_007: "Хүнсний ногоо => Fresh vegetables (including potatoes and root/leafy vegetables).",
            self.G07_008: "Лаазалсан хүнс => Canned and processed food products.",
            self.G07_009: "Ундаа, ус => Non-alcoholic beverages and bottled water.",

            self.G08_001: "Ахуйн цэвэрлэгээний бодис => Household and industrial cleaning agents and detergents.",
            self.G08_002: "Ариун цэврийн цаас => Toilet paper, tissue paper, and similar hygiene paper.",
            self.G08_003: "Саван, угаалгын бодис => Soap, shampoo, and laundry detergents.",
            self.G08_004: "Ариутгалын хэрэгсэл => Disinfection and sanitizing products (alcohol, chlorine, etc.).",
            self.G08_005: "Нэг удаагийн хэрэглээний бүтээгдэхүүн => Disposable hygiene items (gloves, masks, cups, etc.).",

            self.G09_001: "Ажлын хувцас => Workwear and coveralls for staff.",
            self.G09_002: "Дүрэмт хувцас => Uniforms for schools, security, and service staff.",
            self.G09_003: "ХАБЭА хэрэгсэл => Personal protective equipment (PPE) and safety gear.",
            self.G09_004: "Гутал => Safety and field footwear (protective boots, insulated shoes).",
            self.G09_005: "Бээлий => Protective gloves (latex, nitrile, leather, thermal).",

            self.G10_001: "Сурах бичиг => Textbooks for schools and universities.",
            self.G10_002: "Ном => Books and reference materials for libraries and offices.",
            self.G10_003: "Сургалтын хэрэглэгдэхүүн => Teaching and training aids (charts, models, kits).",
            self.G10_004: "Лабораторийн хэрэгсэл => Educational laboratory equipment and consumables.",

            self.G11_001: "Үр, тариалалтын үр => Seeds and planting material (seedlings) for crops.",
            self.G11_002: "Бордоо => Mineral and organic fertilizers for crops.",
            self.G11_003: "Малын тэжээл => Animal feed and concentrates.",
            self.G11_004: "Мал эмнэлгийн эм => Veterinary medicines and related supplies.",
            self.G11_005: "Малын вакцин => Vaccines for livestock.",
            self.G11_006: "ХАА-н химийн бодис => Agro-chemicals (pesticides, herbicides, fungicides).",

            self.G12_001: "Маягт, бланк => Printed forms, blanks, and official templates.",
            self.G12_002: "Сертификат, үнэмлэх => Certificates, ID cards, and secure printed items.",
            self.G12_003: "Сонгуулийн материал => Election materials and kits (ballots, forms, ink).",
            self.G12_004: "Ном, гарын авлага => Manuals, guidebooks, and reference documents.",
            self.G12_005: "Сурталчилгааны хэвлэл => Promotional print materials (brochures, leaflets, posters).",

            self.G13_001: "Гал тогооны тоног төхөөрөмж => Kitchen appliances and cooking equipment.",
            self.G13_002: "Хоол үйлдвэрлэлийн тоног төхөөрөмж => Catering and food production equipment.",
            self.G13_003: "Хөргөлтийн төхөөрөмж => Refrigeration and cold storage equipment.",
            self.G13_004: "Аяга таваг, гал тогооны хэрэгсэл => Kitchen utensils, cookware, and tableware.",
            self.G13_005: "Цэвэрлэгээний тоног төхөөрөмж => Cleaning equipment for kitchens and food areas.",
            self.G13_006: "Хоол үйлдвэрлэлийн сэлбэг, эд анги => Spare parts and consumables for catering equipment.",

            self.G14_001: "Хяналтын камер => CCTV cameras and surveillance systems.",
            self.G14_002: "Хаалга, цоожны систем => Access control systems (electronic locks, card readers).",
            self.G14_003: "Дохиоллын систем => Alarm and intrusion detection systems.",
            self.G14_004: "Биометрийн төхөөрөмж => Biometric security devices (fingerprint, facial recognition).",
            self.G14_005: "Аюулгүй байдлын бусад төхөөрөмж => Other security equipment (metal detectors, scanners).",

            self.G15_001: "Лабораторийн тоног төхөөрөмж => Laboratory instruments and equipment.",
            self.G15_002: "Шинжилгээний урвалж => Laboratory reagents and chemicals.",
            self.G15_003: "Лабораторийн хэрэглэгдэхүүн => Laboratory consumables (slides, pipettes, petri dishes).",
            self.G15_004: "Чанарын хяналтын материал => Quality control materials and standards.",
            self.G15_005: "Лабораторийн сэлбэг, эд анги => Spare parts and accessories for lab equipment.",

            self.G16_001: "Спортын тоног төхөөрөмж => Sports equipment and gear.",
            self.G16_002: "Соёлын тоног төхөөрөмж => Cultural event equipment (sound systems, lighting).",
            self.G16_003: "Арга хэмжээний тоног төхөөрөмж => Event management equipment (stages, tents).",
            self.G16_004: "Үзвэрийн тоног төхөөрөмж => Recreational equipment (playground, music, movie).",
            self.G16_005: "Спортын хувцас, хэрэгсэл => Sportswear and accessories.",

            # Services descriptions
            self.S01_001: "Барилга => Indoor and office building cleaning services.",
            self.S01_002: "Гадна талбай => Outdoor area cleaning (courtyards, roads, snow removal).",
            self.S01_003: "Цонх угаалга => Window and glass facade cleaning services.",

            self.S02_001: "Харуул => Guarding and security post/patrol services.",
            self.S02_002: "Дохиолол => Alarm system installation and monitoring services.",
            self.S02_003: "Камер хяналт => CCTV installation, monitoring, and maintenance services.",

            self.S03_001: "Ачаа тээвэр => Freight and parcel transport and delivery services.",
            self.S03_002: "Зорчигч тээвэр => Passenger transport services (shuttle, bus, school bus).",
            self.S03_003: "Агуулах => Warehousing, storage, and logistics handling services.",

            self.S04_001: "Барилга => Routine building maintenance and minor repair services.",
            self.S04_002: "Тоног төхөөрөмж => Equipment maintenance and repair services.",
            self.S04_003: "Тээврийн хэрэгсэл => Vehicle maintenance and repair services.",

            self.S05_001: "Эрүүл мэнд => Health and medical insurance services.",
            self.S05_002: "Эд хөрөнгө => Property and asset insurance services.",
            self.S05_003: "Авто тээвэр => Motor and vehicle insurance services.",

            self.S06_001: "IT аутсорсинг => Managed IT and outsourced IT operations services.",
            self.S06_002: "Нягтлан бодох => Outsourced accounting and bookkeeping services.",
            self.S06_003: "HR үйлчилгээ => Outsourced HR, payroll, and recruitment services.",

            self.S07_001: "Шуудан үйлчилгээ => Postal mail services.",
            self.S07_002: "Курьер үйлчилгээ => Courier pick-up and delivery services.",
            self.S07_003: "Экспресс хүргэлт => Express and same-day delivery services.",
            self.S07_004: "Баримт бичиг хүргэлт => Secure document delivery services.",
            self.S07_005: "Багц хүргэлт => Parcel and package delivery services.",

            self.S08_001: "Мобайл үйлчилгээ => Mobile telecommunication services (SIM, voice, SMS).",
            self.S08_002: "Дата үйлчилгээ => Data and VPN connectivity services.",
            self.S08_003: "Интернэт үйлчилгээ => Fixed or wireless internet access services.",
            self.S08_004: "IP утас => IP telephony and VoIP services.",
            self.S08_005: "Бусад харилцаа холбоо => Other telecom services (leased lines, trunked radio, etc.).",

            self.S09_001: "Мэргэжлийн сургалт => Professional and technical skills training.",
            self.S09_002: "IT сургалт => IT and digital skills training.",
            self.S09_003: "Аюулгүй байдал, эрүүл ахуй => Safety, health, and HSE training.",
            self.S09_004: "Удирдлагын сургалт => Leadership and management training.",
            self.S09_005: "Бусад сургалт => Other training and capacity-building.",

            self.S10_001: "Захиалгат хөгжүүлэлт => Custom software development services.",
            self.S10_002: "Систем шинэчлэл => System upgrade and modernization services.",
            self.S10_003: "Лиценз нийлүүлэлт => Supply and licensing of software products.",

            self.S11_001: "ERP нэвтрүүлэлт => ERP system implementation and configuration services.",
            self.S11_002: "HRMS => HRMS implementation and support services.",
            self.S11_003: "Санхүүгийн систем => Financial system deployment and support services.",
            self.S11_004: "Нягтлан бодох систем => Accounting system deployment and support services.",

            self.S12_001: "Төрийн портал => Government portal development and operation services.",
            self.S12_002: "Цахим үйлчилгээ => E-service development and rollout services.",
            self.S12_003: "Интеграци => System integration and API development services.",

            self.S13_001: "Регистрийн систем => Registry and master data system development and operation.",
            self.S13_002: "Дата агуулах => Data warehouse design and operation.",
            self.S13_003: "BI систем => Business intelligence and analytics system implementation.",

            self.S14_001: "Security audit => Information security assessment and audit services.",
            self.S14_002: "SOC үйлчилгээ => SOC setup and monitoring services.",
            self.S14_003: "Penetration test => Penetration testing and vulnerability assessment services.",

            self.S15_001: "Cloud үйлчилгээ => Cloud hosting and IaaS/PaaS services.",
            self.S15_002: "Дата төв => Colocation and data center services.",
            self.S15_003: "Backup үйлчилгээ => Backup and disaster recovery (DRaaS) services.",

            self.S16_001: "SLA дэмжлэг => IT support and maintenance under SLA.",
            self.S16_002: "Helpdesk => IT helpdesk and call center support.",
            self.S16_003: "System monitoring => System and network monitoring (NOC) services.",

            self.S17_001: "Бичвэр орчуулга => Written and document translation services.",
            self.S17_002: "Аман орчуулга => Oral and consecutive interpretation services.",
            self.S17_003: "Техникийн орчуулга => Technical and sector-specific translation services.",
            self.S17_004: "Хууль эрх зүйн орчуулга => Legal translation and interpretation services.",
            self.S17_005: "Мэдээллийн орчуулга => Media and content translation/localization services.",

            self.S18_001: "Нийтийн санал асуулга => Public opinion polling and fieldwork.",
            self.S18_002: "Захиалгат судалгаа => Custom and contract research.",
            self.S18_003: "Мэдээлэл цуглуулалт => Data collection and field enumeration.",
            self.S18_004: "Зах зээлийн судалгаа => Market research and consumer studies.",
            self.S18_005: "Нийгмийн судалгаа => Social research and impact studies.",
            
            self.S19_001: "Барилгын ашиглалт => Building operations and facility management services.",
            self.S19_002: "Цахилгаан, сантехник => Electrical and plumbing maintenance services.",
            self.S19_003: "Халаалт, агааржуулалт => Heating, ventilation, and air-conditioning (HVAC) maintenance.",
            self.S19_004: "Лифт үйлчилгээ => Elevator and escalator maintenance services.",
            self.S19_005: "Гадна талбайн арчлалт => Grounds and landscape upkeep services.",

            self.S20_001: "Feasibility study => Feasibility and pre-feasibility study services.",
            self.S20_002: "Cost-benefit analysis => Economic and financial cost-benefit analysis services.",

            self.S21_001: "Судалгаа шинжилгээ => Analytical research study services.",
            self.S21_002: "Үнэлгээ => Program and project evaluation services.",
            
            self.S22_001: "Policy advisory => Policy advisory and policy paper preparation services.",
            self.S22_002: "Strategy consulting => Strategy and organizational consulting services.",
            
            self.S23_001: "Санхүүгийн аудит => Financial audit services.",
            self.S23_002: "IT аудит => IT, system, and process audit services.",
            
            self.S24_001: "PMO => Project management office (PMO) support services.",
            self.S24_002: "Төслийн хяналт => Project supervision and owner's engineer services.",
            
            self.S25_001: "Архитектур => Architectural design and consulting services.",
            self.S25_002: "Инженерийн зураг төсөл => Engineering design and drawing services.",
            
            self.S26_001: "Хэвлэх үйлчилгээ => Printing and press production services.",
            self.S26_002: "Хуулбарлах үйлчилгээ => Copying and duplication services.",
            self.S26_003: "Дизайн, эх бэлтгэл => Graphic design, layout, and prepress services.",
            self.S26_004: "Биндэрлэх, хавтаслах => Binding, finishing, and packaging services.",
            
            self.S27_001: "Сургуулийн хоол үйлдвэрлэл => School meal preparation and catering services.",
            self.S27_002: "Эмнэлгийн хоол үйлдвэрлэл => Hospital and clinical catering services.",
            self.S27_003: "Кейтеринг үйлчилгээ => Event and contract catering services.",
            self.S27_004: "Гал тогооны үйлчилгээний аутсорсинг => Outsourced kitchen operation services.",
            
            self.S28_001: "Хог тээвэрлэлт => Waste collection and transport services.",
            self.S28_002: "Хог ангилан ялгалт => Waste sorting and segregation services.",
            self.S28_003: "Хог булшлах/устгах => Landfill, disposal, and incineration services.",
            self.S28_004: "Дахин боловсруулах үйлчилгээ => Recycling and waste processing services.",
            self.S28_005: "Аюултай хог хаягдал => Hazardous waste handling and treatment services.",
            
            self.S29_001: "Ус хангамжийн үйлчилгээ => Water supply and distribution services.",
            self.S29_002: "Дулааны үйлчилгээ => District heating and steam supply services.",
            self.S29_003: "Цахилгаан хангамжийн үйлчилгээ => Electricity supply and distribution services.",
            self.S29_004: "Суурин холбоо/интернэт үйлчилгээ => Fixed telecommunication and internet services.",
            
            self.S30_001: "Медиа төлөвлөлт, худалдан авалт => Media planning, buying, and placement services.",
            self.S30_002: "Контент үйлдвэрлэл => Media and marketing content production services.",
            self.S30_003: "PR үйлчилгээ => Public relations and communications services.",
            self.S30_004: "Зар сурталчилгааны үйлчилгээ => Advertising and creative campaign services.",
            
            self.S31_001: "Хурал, форум зохион байгуулалт => Conference, forum, and event organization services.",
            self.S31_002: "Тайз, тоноглол түрээс => Stage, sound, and lighting rental services.",
            self.S31_003: "Орчуулга, синхрон орчуулга => Interpretation and simultaneous translation for events.",
            self.S31_004: "Байршил, логистикийн зохион байгуулалт => Venue booking and event logistics services.",
            
            self.S32_001: "Тээврийн хэрэгслийн түрээс => Vehicle rental and short-term lease services.",
            self.S32_002: "Тоног төхөөрөмжийн түрээс => Equipment and machinery rental services.",
            self.S32_003: "Оффис, талбай түрээс => Office and space rental services.",
            self.S32_004: "Лизинг үйлчилгээ => Leasing and finance lease services.",
            
            self.S33_001: "Геологийн судалгаа => Geological surveying and prospecting services.",
            self.S33_002: "Өрөмдлөгийн үйлчилгээ => Drilling services (core, blast, water, etc.).",
            self.S33_003: "Лабораторийн шинжилгээ => Laboratory testing of geological samples.",
            self.S33_004: "Уул уурхайн зөвлөх үйлчилгээ => Mining consulting and feasibility services.",
            
            self.S34_001: "Хууль зүйн зөвлөгөө => Legal advisory and counseling services.",
            self.S34_002: "Гэрээ, баримт бичиг боловсруулах => Contract drafting and legal document review services.",
            self.S34_003: "Шүүхийн төлөөлөл => Legal representation in court and litigation.",
            self.S34_004: "Арбитрын үйлчилгээ => Arbitration, mediation, and dispute resolution services.",

            self.Other: "Other items or services that do not fit in the above codes.",
        }
        return descriptions.get(self, "No description available")

def build_code_reference() -> str:
    """Build a textual catalog of all codes and their descriptions for the LLM."""
    lines: list[str] = []

    lines.append("Tender type codes:")
    for t in TenderType:
        lines.append(f"- {t.value}: {t.description}")

    lines.append("\nLevel-2 category codes:")
    for c in TenderCategory:
        lines.append(f"- {c.value}: {c.description}")

    lines.append("\nLevel-3 detail codes:")
    for item in TenderCategoryItem:
        lines.append(f"- {item.value}: {item.description}")

    return "\n".join(lines)

class BudgetType(str, Enum):
    """Budget funding source classification"""
    STATE_BUDGET = "Төсвийн хөрөнгө"
    OWN_FUNDS = "Өөрийн хөрөнгө"
    LOAN_AID_FUNDING = "Зээл, тусламжийн санхүүжилт"
    PACKAGE_BUDGET = "Багц санхүүжилт"
    CURRENT_BUDGET = "Урсгал төсөв"
    LOCAL_BUDGET = "Орон нутгийн төсөв"

class TenderOverview(BaseModel):
    """Structured summary of a tender plus its classification choices and rationale."""
    summary: str = Field(
        ...,
        title="3-4 sentence Mongolian summary highlighting scope, buyer, key dates, and what is being procured.",
    )
    name: str = Field(..., title="Official tender title as published.")
    selection_number: str = Field(..., title="Published selection/notice number (exact string).")
    ordering_organization: str = Field(..., title="Procuring entity name (ministry/agency/company).")
    announced_date: str = Field(..., title="Notice publication date (YYYY-MM-DD).")
    deadline_date: str = Field(..., title="Bid submission deadline (YYYY-MM-DD).")
    official_link: str = Field(..., title="Public URL to the tender notice.")
    total_budget: Optional[float] = Field(None, title="Total budget or estimate in numeric form; omit if absent.")
    budget_type: Optional[BudgetType] = Field(None, title="Classification of the budget funding source; omit if unknown.")
    type_reason: str = Field(
        ...,
        title="2-3 sentences explaining why the tender is Goods (G), Works (W), Services (S), or Other—cite verbs/nouns from the notice.",
    )
    tender_type: TenderType = Field(..., title="Top-level tender type: Goods (G), Works (W), Services (S), or Other.")
    category_reason: str = Field(
        ...,
        title="2-3 sentences justifying the chosen level-2 code (e.g., W01, G03, S30) using the item being procured and delivery context.",
    )
    tender_category: List[TenderCategory] = Field(
        ...,
        min_length=1,
        title="Level-2 category codes that best classify the main procurement activity (at least one code).",
    )
    category_detail_reason: str = Field(
        ...,
        title="2-3 sentences explaining the selection of level-3 detail codes (e.g., W01-001, G03-002, S30-004; always use level-3 codes like G01-001, not level-2 codes like G01) based on specific items or services being procured.",
    )
    tender_category_detail: List[TenderCategoryItem] = Field(
        ...,
        min_length=1,
        title="Specific level-3 item codes that precisely describe what is being procured (at least one code).",
    )

class TenderOverviewConfig(BaseModel):
    """Model and prompt configuration for generating tender overviews."""
    system_prompt: str = Field(
        default="""You are a tender analysis assistant.
        You will be provided with tender data in Mongolian.
        Generate a concise, informative overview of the tender with the key details defined in the output schema.
        Keep the overview clear and capture only the essential information.
        Write all narrative fields in Mongolian; use English only for code identifiers.

        ### Category rules:
        First, classify the tender into one main type: Goods (G), Services (S), Works (W), or Other.
        Then, based on that main type, pick the appropriate level-2 category codes:
        - Works (W): use W-6 level codes.
        - Goods (G): use G-12 level codes.
        - Services (S): use S-34 level codes.
        Some tenders may span multiple level-2 categories; select all that apply.
        If the tender does not fit any main type or level-2 category, use "Other".
        Use the code descriptions in the enum definitions to resolve ambiguity.
        Finally, assign the specific level-3 detail codes (e.g., W01-001, G01-001, S01-001) under the chosen main category.
        Level-3 codes ALWAYS start with the same prefix as their level-2 code:
        - If you choose W01, allowed level-3 codes are W01-001 ... W01-009 only.
        - If you choose G07, allowed level-3 codes are G07-001 ... G07-009 only.
        - If you choose S30, allowed level-3 codes are S30-001 ... S30-004 only.
        Never mix level-3 codes from a different type or level-2 branch.
        Some tenders may require multiple level-3 codes; in that case, all of them must match one of the selected level-2 prefixes.
        If no level-3 code fits the tender, select "Other".

        ### Quick disambiguation rules (keep it simple):
        - Food as GOODS (buying rice, flour, meat, vegetables, drinks) => G07. Catering/meal SERVICE (cooking/providing meals) => S27.
        - Printing SERVICE (design/printing/copy/binding) => S26. Buying printed items (forms/certificates/books as goods) => G12.
        - IT hardware (devices) => G01. Software development/support as a SERVICE => S10/S16.

        ### Self-check before finalizing:
        - tender_type must match the first letter of every level-2 and level-3 code.
        - Every level-3 code prefix (e.g., G07) must be included in tender_category.
        ### Instructions for rationale fields:
        For each rationale field (type_reason, category_reason, category_detail_reason), provide 2-3 sentences clearly explaining your classification choices.
        Cite specific verbs, nouns, or phrases from the tender data that justify your selections.
        ### Code reference:
        Refer to the code definitions for accurate descriptions. These are the item-level codes.
        If classification is unclear, choose the "Other" code.
        """
    )

    model_name: str = Field(
        default="google-gla:gemini-2.5-pro",
        title="Model Name",
        description="The name of the language model to use for generating the tender overview.",
    )

class TenderOverviewAgent:
    """Thin wrapper around `pydantic_ai.Agent` configured for tender overview generation."""
    config: TenderOverviewConfig
    def __init__(self, config: TenderOverviewConfig):
        self.config = config
        # Enrich the system prompt with an explicit code/description reference
        code_reference = build_code_reference()
        full_system_prompt = f"{self.config.system_prompt}\n\n### Code reference catalog (types, level-2, level-3):\n{code_reference}"
        self.agent = Agent(
            model=self.config.model_name,
            system_prompt=full_system_prompt,
            result_type=TenderOverview,
        )

        self.batch_agent = Agent(
            model=self.config.model_name,
            system_prompt=full_system_prompt,
            result_type=List[TenderOverview],
        )

    async def analyze_tender(self, input_data: dict) -> TenderOverview | None:
        try:
            overview = await self.agent.run([
                str(input_data)
            ])
            return overview.data
        except Exception as e:
            return None
        
    async def analyze_tender_batch(self, input_data_list: List[dict]) -> List[TenderOverview]:
        try:
            overviews = await self.batch_agent.run([
                str(input_data) for input_data in input_data_list
            ])
            return overviews.data
        except Exception as e:
            return []
        
