import re
import textwrap
import streamlit as st

from pathlib import Path
from string import Template
from html import escape


# إعدادات الصفحة
st.set_page_config(
    page_title="نظام حماية المستندات",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ملفات الواجهة
BASE_DIR = Path(_file_).resolve().parent
HTML_PATH = BASE_DIR / "templates.html"
CSS_PATH = BASE_DIR / "style.css"

HTML_CONTENT = HTML_PATH.read_text(encoding="utf-8")


# تحميل القوالب والتنسيقات
def read_template(template_id):
    pattern = (
        r'<template\s+id="'
        + re.escape(template_id)
        + r'"\s*>(.*?)</template>'
    )

    match = re.search(
        pattern,
        HTML_CONTENT,
        flags=re.DOTALL
    )

    if match is None:
        raise ValueError(
            f"القالب '{template_id}' غير موجود في templates.html"
        )

    return textwrap.dedent(match.group(1)).strip()


def render_html(template_id, **values):
    template = Template(read_template(template_id))

    safe_values = {
        key: escape(str(value), quote=True)
        for key, value in values.items()
    }

    st.markdown(
        template.substitute(safe_values),
        unsafe_allow_html=True
    )


def load_styles():
    css_text = CSS_PATH.read_text(encoding="utf-8")
    template = Template(read_template("styles"))

    st.markdown(
        template.substitute(css=css_text),
        unsafe_allow_html=True
    )


def render_banner(title, subtitle, icon):
    render_html(
        "banner",
        title=title,
        subtitle=subtitle,
        icon=icon
    )


def add_spacing(height):
    render_html(
        "spacer",
        height=max(0, int(height))
    )


load_styles()


# حالة الواجهة
ui_defaults = {
    "current_page": "الرئيسية",
    "current_document": None,
    "scan_completed": False,
    "masking_applied": False,
    "masking_view_mode": "masked",
    "extracted_text": None,
    "masked_text": None,
    "scan_results": [],
    "scan_date": None,
    "report_txt": None,
    "report_pdf": None,
    "processing_status": "idle",
    "processing_message": "",
}

for key, default_value in ui_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# إدارة المستند وحالات العرض
def reset_document_view():
    st.session_state.current_document = None
    st.session_state.scan_completed = False
    st.session_state.masking_applied = False
    st.session_state.masking_view_mode = "masked"
    st.session_state.extracted_text = None
    st.session_state.masked_text = None
    st.session_state.scan_results = []
    st.session_state.scan_date = None
    st.session_state.report_txt = None
    st.session_state.report_pdf = None
    st.session_state.processing_status = "idle"
    st.session_state.processing_message = ""


def clear_uploaded_document():
    reset_document_view()
    st.session_state["file_uploader_widget"] = None


def handle_file_selection():
    uploaded_file = st.session_state.get(
        "file_uploader_widget"
    )

    reset_document_view()

    if uploaded_file is None:
        return

    is_txt = uploaded_file.name.lower().endswith(".txt")
    preview_content = ""

    if is_txt:
        preview_content = uploaded_file.getvalue().decode(
            "utf-8",
            errors="replace"
        )

    st.session_state.current_document = {
        "file_name": uploaded_file.name,
        "content": preview_content,
        "file_size": (
            f"{round(uploaded_file.size / 1024, 1)} كيلوبايت"
        ),
        "file_type": (
            "ملف نصي (TXT)" if is_txt else "مستند (PDF)"
        )
    }


def get_document_preview():
    extracted_text = st.session_state.get("extracted_text")

    if extracted_text is not None:
        return extracted_text

    doc = st.session_state.get("current_document")
    return doc.get("content", "") if doc else ""


def render_processing_status():
    status = st.session_state.get(
        "processing_status",
        "idle"
    )
    message = st.session_state.get(
        "processing_message",
        ""
    )

    if status == "loading":
        st.info(message or "جاري معالجة الطلب...")
    elif status == "success":
        st.success(message or "اكتملت العملية بنجاح.")
    elif status == "error":
        st.error(message or "تعذّر إكمال العملية.")


def show_backend_notice():
    st.toast(
        "هذه الواجهة غير مرتبطة بالباك إند بعد.",
        icon="ℹ️"
    )


# القائمة الجانبية
with st.sidebar:
    render_html("sidebar_brand")

    nav_pages = [
        {
            "name": "الرئيسية",
            "icon": "🏠",
            "key": "الرئيسية"
        },
        {
            "name": "فحص المستند",
            "icon": "📄",
            "key": "فحص المستند"
        },
        {
            "name": "تعتيم البيانات",
            "icon": "🔒",
            "key": "تعتيم البيانات"
        },
        {
            "name": "التقرير",
            "icon": "📊",
            "key": "التقرير"
        }
    ]

    for page in nav_pages:
        is_active = (
            st.session_state.current_page == page["key"]
        )

        if st.button(
            f"{page['icon']}  {page['name']}",
            key=f"nav_btn_{page['key']}",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state.current_page = page["key"]
            st.rerun()

    add_spacing(35)

    with st.container(border=True):
        render_html("sidebar_footer")


# الصفحة الرئيسية
def render_home_page():
    render_banner(
        title="نظام حماية المستندات",
        subtitle=(
            "منظومة رقمية متكاملة لفحص وتعتيم البيانات "
            "الحساسة وحفظ سرية المعلومات."
        ),
        icon="🛡️"
    )

    card_data = [
        {
            "icon": "📄",
            "title": "المستندات",
            "desc": "رفع المستندات النصية وملفات PDF بأمان كامل وسرعة عالية.",
            "btn_label": "فتح المستندات",
            "btn_key": "btn_open_documents",
            "card_class": "dash-card-documents",
            "target_page": "فحص المستند"
        },
        {
            "icon": "🔍",
            "title": "فحص المستند",
            "desc": "اكتشاف وتحديد البيانات الحساسة داخل نصوص المستند بدقة.",
            "btn_label": "بدء الفحص",
            "btn_key": "btn_start_scan",
            "card_class": "dash-card-scan",
            "target_page": "فحص المستند"
        },
        {
            "icon": "🔒",
            "title": "تعتيم البيانات",
            "desc": "حماية المعلومات الشخصية وتعتيمها بنجوم وفق معايير الخصوصية.",
            "btn_label": "إدارة التعتيم",
            "btn_key": "btn_manage_masking",
            "card_class": "dash-card-masking",
            "target_page": "تعتيم البيانات"
        },
        {
            "icon": "📊",
            "title": "التقرير الأمني",
            "desc": "استعراض ملخص الفحص وتصدير النتائج الرسمية الموثقة.",
            "btn_label": "عرض التقرير",
            "btn_key": "btn_view_report",
            "card_class": "dash-card-report",
            "target_page": "التقرير"
        }
    ]

    cols = st.columns(4, gap="medium")

    for col, card in zip(cols, card_data):
        with col:
            render_html(
                "card",
                card_class=card["card_class"],
                icon=card["icon"],
                title=card["title"],
                description=card["desc"]
            )

            if st.button(
                card["btn_label"],
                key=card["btn_key"],
                use_container_width=True
            ):
                st.session_state.current_page = card["target_page"]
                st.rerun()

    add_spacing(30)

    _, col_center, _ = st.columns([1, 1.8, 1])

    with col_center:
        if st.button(
            "📤 رفع مستند",
            key="btn_home_start_upload",
            type="primary",
            use_container_width=True
        ):
            st.session_state.current_page = "فحص المستند"
            st.rerun()

    add_spacing(25)

    st.info(
        "🛡️ معاً نحو بيئة رقمية أكثر أماناً — "
        "حماية البيانات مسؤوليتنا جميعاً."
    )


# صفحة فحص المستند
def render_scan_page():
    render_banner(
        title="فحص المستند",
        subtitle=(
            "قم برفع المستند المطلوب لفحصه واكتشاف "
            "البيانات الشخصية والحساسة بدقة."
        ),
        icon="📄"
    )

    st.file_uploader(
        label="اختر ملف من جهازك أو اسحبه إلى الصندوق أدناه (يدعم TXT و PDF):",
        type=["txt", "pdf"],
        key="file_uploader_widget",
        on_change=handle_file_selection
    )

    render_processing_status()

    doc = st.session_state.get("current_document")

    if not doc:
        st.info(
            "يرجى اختيار أو سحب ملف من جهازك "
            "للبدء في إجراءات الفحص."
        )
        return

    with st.container(border=True):
        col_info, col_clear = st.columns([4, 1])

        with col_info:
            st.write(f"📄 *اسم الملف:* {doc['file_name']}")
            st.caption(
                f"الحجم: {doc['file_size']}  |  "
                f"النوع: {doc['file_type']}"
            )

        with col_clear:
            st.button(
                "إلغاء الملف ✕",
                key="btn_clear_doc",
                type="secondary",
                on_click=clear_uploaded_document
            )

    st.subheader(
        f"معاينة محتوى المستند ({doc['file_name']}):"
    )

    if (
        doc["file_type"] == "مستند (PDF)"
        and st.session_state.get("extracted_text") is None
    ):
        st.info(
            "تم اختيار ملف PDF. ستظهر معاينة النص "
            "بعد ربط الواجهة بخدمة استخراج النصوص."
        )

    st.text_area(
        label="محتوى المستند",
        value=get_document_preview(),
        height=260,
        disabled=True,
        label_visibility="collapsed"
    )

    add_spacing(15)

    col_stat, col_btn = st.columns([1.5, 2.5])

    with col_stat:
        status_text = (
            "تم فحص المستند بنجاح ✓"
            if st.session_state.get("scan_completed")
            else "جاهز للفحص"
        )

        st.info(f"حالة الفحص: {status_text}")

    with col_btn:
        if st.button(
            "بدء الفحص واكتشاف البيانات 🔍",
            key="btn_start_scanning",
            type="primary",
            use_container_width=True,
            disabled=(
                st.session_state.get("processing_status")
                == "loading"
            )
        ):
            show_backend_notice()

    if st.session_state.get("scan_completed"):
        st.success(
            "تم الانتهاء من الفحص! "
            "يمكنك الآن الانتقال لتعتيم البيانات."
        )

        _, col_next, _ = st.columns([1, 1.8, 1])

        with col_next:
            if st.button(
                "الانتقال إلى تعتيم البيانات  ➔",
                key="btn_scan_to_masking",
                type="primary",
                use_container_width=True
            ):
                st.session_state.current_page = "تعتيم البيانات"
                st.rerun()


# صفحة تعتيم البيانات
def render_masking_page():
    render_banner(
        title="تعتيم البيانات الحساسة",
        subtitle=(
            "حجب وتشفير البيانات المكتشفة بنجوم "
            "لمنع تسريبها قبل مشاركة المستند."
        ),
        icon="🔒"
    )

    render_processing_status()

    doc = st.session_state.get("current_document")

    if not doc:
        with st.container(border=True):
            render_html(
                "empty_state",
                icon="📂",
                title="مساحة عرض المستند فارغة",
                description=(
                    "لم يتم رفع أي مستند بعد. يرجى التوجه "
                    "إلى فحص المستند ورفع ملف لبدء التعتيم."
                )
            )

        _, col_go, _ = st.columns([1, 1.5, 1])

        with col_go:
            if st.button(
                "الانتقال لرفع مستند الآن ➔",
                key="btn_mask_go_upload",
                type="primary",
                use_container_width=True
            ):
                st.session_state.current_page = "فحص المستند"
                st.rerun()
        return

    original_text = get_document_preview()
    masked_text = st.session_state.get("masked_text")

    masking_applied = (
        st.session_state.get("masking_applied", False)
        and masked_text is not None
    )

    if masking_applied:
        st.success("✓ تم تعتيم وحجب البيانات بنجاح!")

    col_view, col_controls = st.columns([1.8, 1.2])

    with col_view:
        with st.container(border=True):
            st.write(
                f"📄 *المستند:* {doc['file_name']}  |  "
                f"الحجم: {doc['file_size']}"
            )

        if masking_applied:
            is_masked_view = (
                st.session_state.get(
                    "masking_view_mode",
                    "masked"
                ) == "masked"
            )

            displayed_text = (
                masked_text
                if is_masked_view
                else original_text
            )

            box_label = (
                "المستند بعد التعتيم (محمي بنجوم 🔒):"
                if is_masked_view
                else "المستند الأصلي للمراجعة 👁️:"
            )
        else:
            is_masked_view = False
            displayed_text = original_text
            box_label = "المستند الأصلي المرفوع (جاهز للتعتيم 📄):"

        st.subheader(box_label)

        if (
            doc["file_type"] == "مستند (PDF)"
            and st.session_state.get("extracted_text") is None
        ):
            st.info(
                "معاينة النص بانتظار خدمة استخراج النصوص."
            )

        st.text_area(
            label="معاينة التعتيم",
            value=displayed_text,
            height=280,
            disabled=True,
            label_visibility="collapsed"
        )

        add_spacing(12)

        sub1, sub2 = st.columns(2)

        with sub1:
            if st.button(
                "الانتقال إلى التقرير ➔",
                key="btn_mask_go_report",
                type="primary",
                use_container_width=True
            ):
                st.session_state.current_page = "التقرير"
                st.rerun()

        with sub2:
            if st.button(
                "رفع ملف آخر 🔄",
                key="btn_mask_rescan",
                type="secondary",
                use_container_width=True
            ):
                st.session_state.current_page = "فحص المستند"
                st.rerun()

    with col_controls:
        if masking_applied:
            with st.container(border=True):
                st.markdown("### 👁️ خيارات العرض")

                if st.button(
                    "عرض البيانات المعتمة 🔒",
                    key="btn_show_masked",
                    type=(
                        "primary"
                        if is_masked_view
                        else "secondary"
                    ),
                    use_container_width=True
                ):
                    st.session_state.masking_view_mode = "masked"
                    st.rerun()

                if st.button(
                    "إظهار القيمة الأصلية 👁️",
                    key="btn_show_original",
                    type=(
                        "secondary"
                        if is_masked_view
                        else "primary"
                    ),
                    use_container_width=True
                ):
                    st.session_state.masking_view_mode = "original"
                    st.rerun()

        with st.container(border=True):
            st.markdown("### 🛡️ تصنيفات التعتيم")

            st.checkbox(
                "أرقام الهواتف والجوالات",
                value=True,
                key="chk_mask_phones"
            )

            st.checkbox(
                "عناوين البريد الإلكتروني",
                value=True,
                key="chk_mask_emails"
            )

            st.checkbox(
                "أرقام الهوية الوطنية والإقامات",
                value=True,
                key="chk_mask_ids"
            )

            st.checkbox(
                "أسماء الأشخاص والموظفين",
                value=True,
                key="chk_mask_names"
            )

            add_spacing(12)

            if st.button(
                "تطبيق إعدادات التعتيم 🛡️",
                key="btn_apply_masking",
                type="primary",
                use_container_width=True,
                disabled=(
                    st.session_state.get("processing_status")
                    == "loading"
                )
            ):
                show_backend_notice()


# صفحة التقرير
def render_report_page():
    render_banner(
        title="تقرير الفحص والتعتيم الشامل",
        subtitle=(
            "ملخص موثق لنتائج الفحص ومعالجة "
            "البيانات الحساسة وتأكيد الأمان."
        ),
        icon="📊"
    )

    render_processing_status()

    doc = st.session_state.get("current_document