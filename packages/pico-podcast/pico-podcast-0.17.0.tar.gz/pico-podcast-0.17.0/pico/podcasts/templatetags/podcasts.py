from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe
from markdown import markdown as md
import re


NEW_SPEAKER_EX = r'^\[([\d:]+)\] (.+): (.+)$'
SAME_SPEAKER_EX = r'^\[([\d:]+)\] (.+)$'


register = Library()


@register.filter()
def markdown(value, style='default'):
    kwargs = settings.MARKDOWN_STYLES.get(style, {})
    kwargs.update(
        {
            'output_format': 'html'
        }
    )

    if value and str(value).strip():
        return mark_safe(
            md(
                str(value),
                **kwargs
            )
        )

    return ''


@register.filter()
def transcript(value):
    lines = []
    current_speaker = None
    speakers = []

    for line in value.splitlines():
        if not line.strip():
            lines.append('')
            continue

        match = re.match(NEW_SPEAKER_EX, line)
        if match is not None:
            time, speaker, text = match.groups()
            if speaker not in speakers:
                speakers.append(speaker)

            speaker_index = speakers.index(speaker) + 1
            lines.append(
                (
                    '<div class="transcript-line transcript-speaker-%d">'
                    '<code class="transcript-timecode">%s</code>'
                    '<span class="transcript-speaker">%s</span>'
                    '<div class="transcript-speech">%s</div>'
                    '</div>'
                ) % (
                    speaker_index,
                    time,
                    speaker,
                    text
                )
            )

            current_speaker = speaker
            continue

        match = re.match(SAME_SPEAKER_EX, line)
        if match is not None and current_speaker is not None:
            time, text = match.groups()
            lines.append(
                (
                    '<div class="transcript-line transcript-speaker-same">'
                    '<code class="transcript-timecode">%s</code>'
                    '<span class="transcript-speaker"></span>'
                    '<div class="transcript-speech">%s</div>'
                    '</div>'
                ) % (
                    time,
                    text
                )
            )

            continue

        lines.append(
            markdown(line)
        )

        current_speaker = None

    return mark_safe('\n'.join(lines))
