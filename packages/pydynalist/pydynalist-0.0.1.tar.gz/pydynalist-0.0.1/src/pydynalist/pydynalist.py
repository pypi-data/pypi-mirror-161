import requests
import logging

logger = logging.getLogger(__name__)


class Dynalist:
    def __init__(self, token):
        self.token = token

    def valid_token(self, token=None) -> bool:
        if not token:
            token = self.token
        res = requests.post("https://dynalist.io/api/v1/file/list", json={"token": token})
        data = res.json()
        if data["_code"] == "Ok":
            return True
        else:
            return False

    @property
    def docs(self) -> list:
        res = requests.post("https://dynalist.io/api/v1/file/list", json={"token": self.token})
        data = res.json()
        if data["_code"] == "Ok":
            docs = []
            for dic in data["files"]:
                if dic["type"] == "document":
                    docs.append(dic)
            return docs
        else:
            logger.error(f"Get docs: {data}")
            return []

    @property
    def folders(self) -> list:
        res = requests.post("https://dynalist.io/api/v1/file/list", json={"token": self.token})
        data = res.json()
        if data["_code"] == "Ok":
            folders = []
            for dic in data["files"]:
                if dic["type"] == "folder":
                    folders.append(dic)
            return folders
        else:
            logger.error(f"Get folders: {data}")
            return []

    def get_doc(self, doc_id: str) -> dict:
        res = requests.post(
            "https://dynalist.io/api/v1/doc/read",
            json={"token": self.token, "file_id": doc_id},
        )
        data = res.json()
        if data["_code"] == "Ok":
            nodes = res.json()["nodes"]
            doc_dict = {n["id"]: n for n in nodes}
            return doc_dict
        else:
            logger.error(f"Get doc: {data}")
            return {}

    def get_doc_id(self, name: str):
        titles, docs_ids = self.get_docs_titles_and_ids()
        for i, title in enumerate(titles):
            if name == title:
                return docs_ids[i]
        return None

    def get_doc_title(self, doc_id: str):
        titles, docs_ids = self.get_docs_titles_and_ids()
        for i, id in enumerate(docs_ids):
            if id == doc_id:
                return titles[i]
        return None

    def get_docs_titles_and_ids(self) -> list:
        docs = self.docs
        titles = []
        doc_ids = []
        for doc in docs:
            title = doc.get("title", None)
            titles.append(title)
            doc_id = doc.get("id", None)
            doc_ids.append(doc_id)
        return titles, doc_ids

    def send_to_inbox(self, content: str, note: str) -> bool:
        res = requests.post(
            "https://dynalist.io/api/v1/inbox/add",
            json={"token": self.token, "index": None, "content": content, "note": note},
        )
        data = res.json()
        if data["_code"] == "Ok":
            return True
        else:
            return False

    def edit_doc(self, file_id: str, changes: list) -> dict:
        res = requests.post(
            "https://dynalist.io/api/v1/doc/edit",
            json={"token": self.token, "file_id": file_id, "changes": changes},
        )
        data = res.json()
        return data

    # action: "edit", "move", "insert", "delete"
    @staticmethod
    def prepare_changes(
        action,
        changes=[],
        content=None,
        note=None,
        node_id=None,
        parent_id=None,
        index=None,
        checkbox=None,
        checked=None,
        heading=None,
        color=None,
    ) -> list:
        change = {"action": action}
        if content != None:
            change["content"] = content
        if note != None:
            change["note"] = note
        if node_id != None:
            change["node_id"] = node_id
        if parent_id != None:
            change["parent_id"] = parent_id
        if index != None:
            change["index"] = index
        if checkbox != None:
            change["checkbox"] = checkbox
        if checked != None:
            change["checked"] = checked
        if heading != None:
            change["heading"] = heading
        if color != None:
            change["color"] = color
        changes.append(change)
        return changes

    @staticmethod
    def recurcively_analize_doc(doc: dict, func, *args, **kwargs):
        children_list = []
        tab = 0
        if "children" in doc.keys():
            for r_c in doc["root"]["children"]:
                children_list.append(r_c)
        else:
            children_list.append("root")
        for rid, rnest in doc.items():
            if rid in children_list:  # do not print children as duplicates
                func(doc=doc, id=rid, nest=rnest, tab=tab, *args, **kwargs)
                if "children" in rnest.keys():
                    for cid in rnest["children"]:
                        Dynalist._recursevily_analize_node(doc, cid, tab, func, *args, **kwargs)

    @staticmethod
    def _recursevily_analize_node(doc: dict, cid: str, tab: int, func, *args, **kwargs):
        for rid, rnest in doc.items():  # first loop
            if cid == rid:
                if "children" in rnest.keys():
                    func(doc=doc, id=cid, nest=rnest, tab=tab, *args, **kwargs)
                    tab += 1
                    for id in rnest["children"]:  # secon loop
                        Dynalist._recursevily_analize_node(doc, id, tab, func, *args, **kwargs)
                    tab -= 1
                else:
                    func(doc=doc, id=cid, nest=rnest, tab=tab, *args, **kwargs)

    @staticmethod
    def func_parse_data_from_node_to_dict(nest, *args, **kwargs):
        if "dictionary" not in kwargs.keys():
            raise ValueError(f"Missing 'dictionary' in kwargs={kwargs}")
        dictionary = kwargs.get("dictionary")
        tab = kwargs.get("tab", None)
        note = nest.get("note", None)
        node_id = nest.get("id", None)
        content = nest.get("content", None)
        checkbox = nest.get("checkbox", None)
        checked = nest.get("checked", None)
        heading = nest.get("heading", None)
        color = nest.get("color", None)

        dictionary[node_id] = {
            "content": content,
            "note": note,
            "tab": tab,
            "checkbox": checkbox,
            "checked": checked,
            "heading": heading,
            "color": color,
        }
