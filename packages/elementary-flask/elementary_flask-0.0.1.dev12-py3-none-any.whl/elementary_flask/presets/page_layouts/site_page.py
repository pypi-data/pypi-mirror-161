from types import SimpleNamespace

from elementary_flask.components import EmptyPageLayout


class AbstractSitePageLayout(EmptyPageLayout):
    def __init__(self, additional_includes=None, navigation=None):
        super(AbstractSitePageLayout, self).__init__(additional_includes=additional_includes,
                                                     block_names=['main', 'aside'])
        self.navigation = navigation

    def render_body_tag(self, ns: SimpleNamespace) -> str:
        body = '<body>'

        # Header & navigation
        body += self.render_header(ns) + self.render_nav(ns)

        # Page content
        for el in ('main', 'aside'):
            if el in ns.rendered_blocks and ns.rendered_blocks[el]:
                body += f'<{el}>{ns.rendered_blocks[el]}</{el}>'

        # Footer
        body += self.render_footer(ns)

        # Body includes
        if ns.component_includes:
            body += ns.component_includes.render_body_includes()
        body += '</body>'
        return body

    def render_header(self, ns: SimpleNamespace) -> str:
        raise NotImplementedError()

    def render_nav(self, ns: SimpleNamespace) -> str:
        raise NotImplementedError()

    def render_footer(self, ns: SimpleNamespace) -> str:
        raise NotImplementedError()


class SitePageLayout(AbstractSitePageLayout):
    def render_header(self, ns: SimpleNamespace) -> str:
        pass

    def render_nav(self, ns: SimpleNamespace) -> str:
        if self.navigation:
            return self.navigation.render(**ns.__dict__)

    def render_footer(self, ns: SimpleNamespace) -> str:
        pass

    def __init__(self, additional_includes=None, navigation=None):
        super(SitePageLayout, self).__init__(additional_includes=additional_includes,
                                             navigation=navigation)
