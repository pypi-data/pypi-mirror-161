from collective.tiles.carousel import _
from plone import api
from plone.app.contenttypes.browser.link_redirect_view import NON_RESOLVABLE_URL_SCHEMES
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from Products.Five import BrowserView


class SlideView(BrowserView):
    def __call__(self, item, data):
        self.update(item, data)
        return self.index()

    def update(self, item, data):
        self.item = self.get_item_info(item, data)

    def get_item_info(self, obj, data):
        item = {}
        item["title"] = obj.title
        item["description"] = obj.description
        item["img_tag"] = self.get_tag(obj, data)
        item["link"] = self.get_link(obj, data)
        item["type"] = obj.portal_type
        item["data"] = data
        return item

    def get_tag(self, obj, data):
        scale_util = api.content.get_view("images", obj, self.request)
        return scale_util.tag(
            fieldname="image",
            mode=data.get("crop") and "cover" or "keep",
            scale=(
                data.get("image_scale")
                if data.get("image_scale", "") != "original"
                else None
            ),
            css_class=data.get("image_class"),
            alt=obj.description or obj.title,
        )

    def _url_uses_scheme(self, schemes, url=None):
        for scheme in schemes:
            if url.startswith(scheme):
                return True
        return False

    def get_link(self, obj, data):
        """Get target for linked slide."""

        # no linking
        if data.get("link_slides") == "disabled":
            return

        # link to parent
        if data.get("link_slides") == "collection":
            return obj.aq_parent.absolute_url()

        else:
            # link to external urls
            if getattr(obj, "remoteUrl", None):
                # Returns the url with link variables replaced.
                url = replace_link_variables_by_paths(obj, obj.remoteUrl)

                if self._url_uses_scheme(NON_RESOLVABLE_URL_SCHEMES, url=obj.remoteUrl):
                    # For non http/https url schemes, there is no path to resolve.
                    return url

                if url.startswith("."):
                    # we just need to adapt ../relative/links, /absolute/ones work
                    # anyway -> this requires relative links to start with ./ or
                    # ../
                    context_state = self.context.restrictedTraverse(
                        "@@plone_context_state"
                    )
                    url = "/".join([context_state.canonical_object_url(), url])
                else:
                    if not url.startswith(("http://", "https://")):
                        url = self.request["SERVER_URL"] + url
                return url

            # link to first related item
            if (
                len(getattr(obj, "relatedItems", [])) > 0
                and obj.relatedItems[0].to_object
            ):
                return obj.relatedItems[0].to_object.absolute_url()

            # link to object
            else:
                return obj.absolute_url()
