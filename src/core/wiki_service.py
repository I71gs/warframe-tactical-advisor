from urllib.parse import quote


class WikiService:

    def get_article_url(
        self,
        article_name
    ):

        safe_name = quote(
            article_name.replace(
                " ",
                "_"
            )
        )

        return (
            "https://warframe.fandom.com/wiki/"
            + safe_name
        )