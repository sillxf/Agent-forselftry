from pathlib import Path


def load_documents():

    docs=[]

    path = Path(__file__).resolve().parent.parent / "knowledge"

    for file in path.glob("*.md"):

        text=file.read_text(
            encoding="utf-8"
        )

        docs.append(
            {
                "filename":
                file.name,

                "content":
                text
            }
        )

    return docs