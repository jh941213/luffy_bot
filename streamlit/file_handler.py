import pandas as pd
import PyPDF2
import markdown

def handle_uploaded_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        with PyPDF2.PdfReader(uploaded_file) as reader:
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
        return df

    elif uploaded_file.type == "text/markdown":
        content = uploaded_file.read().decode("utf-8")
        return markdown.markdown(content)

    else:
        return "Unsupported file type."
