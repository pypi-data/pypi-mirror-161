from markdown import markdown


class HandlerBase(object):
    self_closing = True

    def handle(self, value):
        raise NotImplementedError('Method not implemented')

    def markdown(self, value):
        return markdown(value)

    def parse_contents(self, value, to_markdown=False):
        from . import tags

        parsed = tags.parse(value)
        if to_markdown:
            parsed = self.markdown(parsed)

        return parsed
