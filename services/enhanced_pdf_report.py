"""
Enhanced PDF Report Generator

This module provides a completely redesigned PDF report generator with modern styling,
better alignment, and professional visual elements for DataGuardian Pro reports.
"""

import os
import io
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import base64

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, Frame, PageTemplate, NextPageTemplate, Flowable, 
    KeepTogether, ListFlowable, ListItem
)
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

# Configure logging
logger = logging.getLogger(__name__)

# DataGuardian Pro logo as base64 SVG
LOGO_SVG_BASE64 = """
PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjU2IiB2aWV3Qm94PSIwIDAgMjAwIDU2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogICAgPHBhdGggZD0iTTI0LjUgOEMxNS45Mzk2IDggOSAxNC45Mzk2IDkgMjMuNUM5IDMyLjA2MDQgMTUuOTM5NiAzOSAyNC41IDM5QzMzLjA2MDQgMzkgNDAgMzIuMDYwNCA0MCAyMy41QzQwIDE0LjkzOTYgMzMuMDYwNCA4IDI0LjUgOFoiIGZpbGw9IiMyNTYzRUIiLz4KICAgIDxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiBkPSJNMjQuNSAxMkMxOC4xNDg3IDEyIDEzIDE3LjE0ODcgMTMgMjMuNUMxMyAyOS44NTEzIDE4LjE0ODcgMzUgMjQuNSAzNUMzMC44NTEzIDM1IDM2IDI5Ljg1MTMgMzYgMjMuNUMzNiAxNy4xNDg3IDMwLjg1MTMgMTIgMjQuNSAxMlpNMTkgMjAuNUMxOSAxOS4xMTkzIDIwLjExOTMgMTggMjEuNSAxOEMyMi44ODA3IDE4IDI0IDE5LjExOTMgMjQgMjAuNUMyNCAyMS44ODA3IDIyLjg4MDcgMjMgMjEuNSAyM0MyMC4xMTkzIDIzIDE5IDIxLjg4MDcgMTkgMjAuNVpNMjcuNSAxOEMyNi4xMTkzIDE4IDI1IDE5LjExOTMgMjUgMjAuNUMyNSAyMS44ODA3IDI2LjExOTMgMjMgMjcuNSAyM0MyOC44ODA3IDIzIDMwIDIxLjg4MDcgMzAgMjAuNUMzMCAxOS4xMTkzIDI4Ljg4MDcgMTggMjcuNSAxOFpNMTggMjYuNUMxOCAyNS42NzE2IDE4LjY3MTYgMjUgMTkuNSAyNUgyOS41QzMwLjMyODQgMjUgMzEgMjUuNjcxNiAzMSAyNi41QzMxIDI3LjMyODQgMzAuMzI4NCAyOCAyOS41IDI4SDE5LjVDMTguNjcxNiAyOCAxOCAyNy4zMjg0IDE4IDI2LjVaIiBmaWxsPSJ3aGl0ZSIvPgogICAgPHBhdGggZD0iTTQ3LjU1MiAxOC4ySDUyLjg4QzU0Ljc4NCAxOC4yIDU2LjE4NCAxOC42NjQgNTcuMDggMTkuNTkyQzU3Ljk3NiAyMC41MDQgNTguNDI0IDIxLjg0OCA1OC40MjQgMjMuNjI0QzU4LjQyNCAyNS40MzIgNTcuOTc2IDI2LjggNTcuMDggMjcuNzI4QzU2LjE4NCAyOC42NTYgNTQuNzg0IDI5LjEyIDUyLjg4IDI5LjEySDQ3LjU1MlYxOC4yWk01Mi43ODQgMjcuMjI0QzU0LjAzMiAyNy4yMjQgNTQuOTY4IDI2LjkxMiA1NS41OTIgMjYuMjg4QzU2LjIxNiAyNS42NjQgNTYuNTI4IDI0Ljc3NiA1Ni41MjggMjMuNjI0QzU2LjUyOCAyMi40ODggNTYuMjE2IDIxLjYwOCA1NS41OTIgMjAuOTg0QzU0Ljk2OCAyMC4zNiA1NC4wMzIgMjAuMDQ4IDUyLjc4NCAyMC4wNDhINDkuNFYyNy4yMjRINTIuNzg0Wk02MC45OTkzIDIxLjQ2NEg2Mi41MzUzTDYyLjY1OTMgMjIuNjE2QzYyLjkxMTMgMjIuMjMyIDYzLjI1OTMgMjEuOTI4IDYzLjcwMzMgMjEuNzA0QzY0LjE0NzMgMjEuNDggNjQuNjI3MyAyMS4zNjggNjUuMTQzMyAyMS4zNjhDNjUuOTc1MyAyMS4zNjggNjYuNjE5MyAyMS42MDggNjcuMDc1MyAyMi4wODhDNjcuNTMxMyAyMi41NjggNjcuNzU5MyAyMy4zMTIgNjcuNzU5MyAyNC4zMlYyOS4xMkg2Ni4wNzUzVjI0LjMyQzY2LjA3NTMgMjIuOTM2IDY1LjQ1OTMgMjIuMjY0IDY0LjIyNzMgMjIuMzA0QzYzLjc2NzMgMjIuMzA0IDYzLjM3MTMgMjIuNDA4IDYzLjAzOTMgMjIuNjE2QzYyLjcwNzMgMjIuODI0IDYyLjQ1NTMgMjMuMTA0IDYyLjI4MzMgMjMuNDU2VjI5LjEySDYwLjU5OTNWMjEuNDY0SDYwLjk5OTNaTTcwLjIzODQgMjEuNDY0SDcxLjc3NDRMNzEuODk4NCAyMi41NjhDNzIuMTUwNCAyMi4yIDcyLjQ4NjQgMjEuOTA0IDcyLjkwNjQgMjEuNjhDNzMuMzI2NCAyMS40NTYgNzMuNzkwNCAyMS4zNDQgNzQuMjk4NCAyMS4zNDRDNzUuMzMwNCAyMS4zNDQgNzYuMDg2NCAyMS42NjQgNzYuNTY2NCAyMi4zMDRDNzYuODE4NCAyMS45NjggNzcuMTc4NCAyMS42OCA3Ny42NDY0IDIxLjQ0Qzc4LjExNDQgMjEuMiA3OC42MDY0IDIxLjA4IDc5LjEyMjQgMjEuMDhDNzkuOTYyNCAyMS4wOCA4MC42MjI0IDIxLjMyOCA4MS4xMDI0IDIxLjgyNEM4MS41ODI0IDIyLjMyIDgxLjgyMjQgMjMuMDg4IDgxLjgyMjQgMjQuMTI4VjI5LjEySDgwLjEzODRWMjQuMkM4MC4xMzg0IDIyLjg4OCA3OS41NjI0IDIyLjIzMiA3OC40MTA0IDIyLjIzMkM3Ny45OTA0IDIyLjIzMiA3Ny42MzA0IDIyLjMzNiA3Ny4zMzA0IDIyLjU0NEM3Ny4wMzA0IDIyLjc1MiA3Ni44MDI0IDIzLjAyNCA3Ni42NDY0IDIzLjM2Qzc2LjY0NjQgMjMuNDg4IDc2LjY0NjQgMjMuNiA3Ni42NDY0IDIzLjY5NkM3Ni42NjI0IDIzLjc5MiA3Ni42NzA0IDIzLjg2NCA3Ni42NzA0IDIzLjkxMlYyOS4xMkg3NC45ODY0VjI0LjIyNEM3NC45ODY0IDIyLjkxMiA3NC40MTA0IDIyLjI1NiA3My4yNTg0IDIyLjI1NkM3Mi44Mzg0IDIyLjI1NiA3Mi40Nzg0IDIyLjM2IDcyLjE3ODQgMjIuNTY4QzcxLjg3ODQgMjIuNzYgNzEuNjU4NCAyMy4wMjQgNzEuNTE4NCAyMy4zNlYyOS4xMkg2OS44MzQ0VjIxLjQ2NEg3MC4yMzg0Wk05MS4yMjY2IDIxLjQ2NFYyOS4xMkg4OS42OTA2TDg5LjU2NjYgMjcuOTJDODkuMzE0NiAyOC4zMDQgODguOTYyNiAyOC42MTYgODguNTEwNiAyOC44NTZDODguMDU4NiAyOS4wOCA4Ny41NjY2IDI5LjE5MiA4Ny4wMzQ2IDI5LjE5MkM4Ni4xMDY2IDI5LjE5MiA4NS4zNzA2IDI4Ljg5NiA4NC44MjY2IDI4LjMwNEM4NC4yOTg2IDI3LjcxMiA4NC4wMzQ2IDI2LjggODQuMDM0NiAyNS41NjhWMjEuNDY0SDg1LjcxODZWMjUuNTY4Qzg1LjcxODYgMjYuMjg4IDg1Ljg1MDYgMjYuOCA4Ni4xMTQ2IDI3LjEwNEM4Ni4zNzg2IDI3LjQwOCA4Ni43OTQ2IDI3LjU2IDg3LjM2MjYgMjcuNTZDODcuODM4NiAyNy41NiA4OC4yNTA2IDI3LjQ1NiA4OC41OTg2IDI3LjI0OEM4OC45NDY2IDI3LjA0IDg5LjE5ODYgMjYuNzM2IDg5LjM1NDYgMjYuMzM2VjIxLjQ2NEg5MS4yMjY2Wk05NS4wNzk3IDI2LjQ1Nkw5NC45MzE3IDI3LjI5NkM5NS4yMTU3IDI3LjQ3MiA5NS41NDc3IDI3LjYwOCA5NS45Mjc3IDI3LjcwNEM5Ni4zMjM3IDI3Ljc4NCA5Ni43MTk3IDI3LjgyNCA5Ny4xMTU3IDI3LjgyNEM5Ny44Mjc3IDI3LjgyNCA5OC4zMzU3IDI3LjcyIDk4LjYzOTcgMjcuNTEyQzk4Ljk1OTcgMjcuMzA0IDk5LjExOTcgMjcuMDI0IDk5LjExOTcgMjYuNjcyQzk5LjExOTcgMjYuMzg0IDk4Ljk4MzcgMjYuMTYgOTguNzExNyAyNkM5OC40Mzk3IDI1LjgyNCA5Ny45MTU3IDI1LjY0OCA5Ny4xMzk3IDI1LjQ3MkM5Ni4xODc3IDI1LjI2NCA5NS41MDc3IDI0Ljk3NiA5NS4wOTk3IDI0LjYwOEM5NC42OTE3IDI0LjI0IDk0LjQ4NzcgMjMuNzQ0IDk0LjQ4NzcgMjMuMTJDOTQuNDg3NyAyMi4zNTIgOTQuNzY3NyAyMS43NjggOTUuMzI3NyAyMS4zNjhDOTUuODg3NyAyMC45NTIgOTYuNjcxNyAyMC43NDQgOTcuNjc5NyAyMC43NDRDOTguMTA3NyAyMC43NDQgOTguNTE1NyAyMC43NzYgOTguOTAzNyAyMC44NEM5OS4zMDc3IDIwLjkwNCA5OS42Nzk3IDIxIDEwMC4wMiAyMS4xMjhMOTkuODQ3NyAyMi4wMTZDOTkuNDY3NyAyMS44NTYgOTkuMTIzNyAyMS43MzYgOTguODE1NyAyMS42NTZDOTguNTIzNyAyMS41NzYgOTguMTg3NyAyMS41MzYgOTcuODA3NyAyMS41MzZDOTcuMTc1NyAyMS41MzYgOTYuNzAzNyAyMS42NCA5Ni4zOTU3IDIxLjg0OEM5Ni4wODc3IDIyLjA1NiA5NS45MzU3IDIyLjMyOCA5NS45MzU3IDIyLjY2NEM5NS45MzU3IDIyLjk4NCA5Ni4wODc3IDIzLjIzMiA5Ni4zOTE3IDIzLjQwOEM5Ni43MTE3IDIzLjU4NCA5Ny4yODM3IDIzLjc2IDk4LjEwNzcgMjMuOTM2Qzk5LjA0MzcgMjQuMTI4IDk5LjY5NTcgMjQuNCA5MC4wQzEwMC40MzIgMjUuMTA0IDEwMC42MiAyNS42MDggMTAwLjYyIDI2LjI2NEMxMDAuNjIgMjcuMDQ4IDEwMC4zMjQgMjcuNjQ4IDk5LjczMTcgMjguMDY0Qzk5LjEzOTcgMjguNDggOTguMzIzNyAyOC42ODggOTcuMjgzNyAyOC42ODhDOTYuNzY3NyAyOC42ODggOTYuMjkxNyAyOC42NDggOTUuODU1NyAyOC41NjhDOTUuNDM1NyAyOC40ODggOTUuMDU1NyAyOC4zNzYgOTQuNzE1NyAyOC4yMzJMOTUuMDc5NyAyNi40NTZaTTEwNi4zMTggMjEuMzY4QzEwNy4xODIgMjEuMzY4IDEwNy44NjIgMjEuNjggMTA4LjM1OCAyMi4zMDRDMTA4Ljg3IDIyLjkxMiAxMDkuMTI2IDIzLjgzMiAxMDkuMTI2IDI1LjA2NEMxMDkuMTI2IDI2LjM2IDEwOC44NyAyNy4zMjggMTA4LjM1OCAyNy45NjhDMTA3Ljg0NiAyOC41OTIgMTA3LjE2NiAyOC45MDQgMTA2LjMxOCAyOC45MDRDMTA1LjgyMiAyOC45MDQgMTA1LjM3NCAyOC44IDEwNC45NzQgMjguNTkyQzEwNC41OSAyOC4zODQgMTA0LjI4NiAyOC4xMDQgMTA0LjA2MiAyNy43NTJWMTFMZTM0SDEwMi4zNzhWMjEuNDY0SDEwMy45MTRMMTAubS4wMzggMjIuNjRDMTA0LjI2MiAyMi4yNCAxMDQuNTY2IDIxLjkyOCAxMDQuOTUgMjEuNzA0QzEwNS4zNSAyMS40OCAxMDUuODA2IDIxLjM2OCAxMDYuMzE4IDIxLjM2OFpNMTA1Ljg2MiAyNy4zNjhDMTA2LjM3IDI3LjM2OCAxMDYuNzU4IDI3LjE3NiAxMDcuMDI2IDI2Ljc5MkMxMDcuMjk0IDI2LjQwOCAxMDcuNDM4IDI1LjgzMiAxMDcuNDU4IDI1LjA2NEMxMDcuNDU4IDI0LjI5NiAxMDcuMzEgMjMuNzQ0IDEwNy4wMSAyMy40MDhDMTA2LjcyNiAyMy4wNTYgMTA2LjMzOCAyMi44OCAxMDUuODQ2IDIyLjg4QzEwNS4zODYgMjIuODggMTA1LjAwNiAyMi45ODQgMTA0LjcwMiAyMy4xOTJDMTA0LjM5OCAyMy40IDEwNC4xNzQgMjMuNzA0IDEwNC4wMyAyNC4xMDRWMjYuMjY0QzEwNC4xNzQgMjYuNjQ4IDEwNC4zOTggMjYuOTI4IDEwNC43MDIgMjcuMTA0QzEwNS4wMDYgMjcuMjggMTA1LjM4NiAyNy4zNjggMTA1Ljg2MiAyNy4zNjhaTTExMy42OTcgMjEuNDY0SDExNS4yMzNMMTE1LjM1NyAyMi42MTZDMTEcLjYwOSAyMi4yMzIgMTE1Ljk1NyAyMS45MjggMTE2LjQwMSAyMS43MDRDMTbjLjg0NSAyMS40OCAxMTcuMzI1IDIxLjM2OCAxMTcuODQxIDIxLjM2OEMxMTguNjczIDIxLjM2OCAxMTkuMzE3IDIxLjYwOCAxMTkuNzczIDIyLjA4OEMxMjAuMjI5IDIyLjU2OCAxMjAuNDU3IDIzLjMxMiAxMjAuNDU3IDI0LjMyVjI5LjEySDExOC43NzNWMjQuMzJDMTE4Ljc3MyAyMi45MzYgMTE4LjE1NyAyMi4yNjQgMTE2LjkyNSAyMi4zMDRDMTE2LjQ2NSAyMi4zMDQgMTE2LjA2OSAyMi40MDggMTE1LjczNyAyMi42MTZDMTEmr40NSAyMi44MjQgMTE1LjE1MyAyMy4xMDQgMTE0Ljk4MSAyMy40NTZWMjkuMTJIMTEzLjI5N1YyMS40NjRIMTEzLjY5N1pNMTI4LjM5MyAyNi40NTZMMTI4LjI0NSAyNy4yOTZDMTI4LjUyOSAyNy40NzIgMTI4Ljg2MSAyNy42MDggMTI5LjI0MSAyNy43MDRDMTIo. NjM3IDI3Ljc4NCAxMzAuMDMzIDI3LjgyNCAxMzAuNDI5IDI3LjgyNEMxMzEuMTQxIDI3LjgyNCAxMzEuNjQ5IDI3LjcyIDEzMS45NTMgMjcuNTEyQzEzMi4yNzMgMjcuMzA0IDEzMi40MzMgMjcuMDI0IDEzMi40MzMgMjYuNjcyQzEzMi40MzMgMjYuMzg0IDEzMi4yOTcgMjYuMTYgMTMyLjAyNSAyNkMxMzEuNzUzIDI1LjgyNCAxMzEuMjI5IDI1LjY0OCAxMzAuNDUzIDI1LjQ3MkMxMjkuNTAxIDI1LjI2NCAxMjguODIxIDI0Ljk3NiAxMjguNDEzIDI0LjYwOEMxMjguMDA1IDI0LjI0IDEyNy44MDEgMjMuNzQ0IDEyNy44MDEgMjMuMTJDMTI3LjgwMSAyMi4zNTIgMTI4LjA4MSAyMS43NjggMTI4LjY0MSAyMS4zNjhDMTI5LjIwMSAyMC45NTIgMTI5Ljk4NSAyMC43NDQgMTMwLjk5MyAyMC43NDRDMTMxLjQyMSAyMC43NDQgMTMxLjgyOSAyMC43NzYgMTMyLjIxNyAyMC44NEMxMzIuNjIxIDIwLjkwNCAxMzIuOTkzIDIxIDEzMy4zMzMgMjEuMTI4TDEzMy4xNjEgMjIuMDE2QzEzMi43ODEgMjEuODU2IDEzMi40MzcgMjEuNzM2IDEzMi4xMjkgMjEuNjU2QzEzMS44MzcgMjEuNTc2IDEzMS41MDEgMjEuNTM2IDEzMS4xMjEgMjEuNTM2QzEzMC40ODkgMjEuNTM2IDEzMC4wMTcgMjEuNjQgMTI5LjcwOSAyMS44NDhDMTI5LjQwMSAyMi4wNTYgMTI5LjI0OSAyMi4zMjggMTI5LjI0OSAyMi42NjRDMTI5LjI0OSAyMi45ODQgMTI5LjQwMSAyMy4yMzIgMTI5LjcwNSAyMy40MDhDMTMwLjAyNSAyMy41ODQgMTMwLjU5NyAyMy43NiAxMzEuNDIxIDIzLjkzNkMxMzIuMzU3IDI0LjEyOCAxMzMuMDA5IDI0LjQgMTMzLjM2OSAyNC43NTJDMTMzLjc0NSAyNS4xMDQgMTMzLjkzMyAyNS42MDggMTMzLjkzMyAyNi4yNjRDMTMzLjkzMyAyNy4wNDggMTMzLjYzNyAyNy42NDggMTMzLjA0NSAyOC4wNjRDMTMyLjQ1MyAyOC40OCAxMzEuNjM3IDI4LjY4OCAxMzAuNTk3IDI4LjY4OEMxMzAuMDgxIDI4LjY4OCAxMjkuNjA1IDI4LjY0OCAxMjkuMTY5IDI4LjU2OEMxMjguNzQ5IDI4LjQ4OCAxMjguMzY5IDI4LjM3NiAxMjguMDI5IDI4LjIzMkwxMjguMzkzIDI2LjQ1NlpNMTQwLjk1OSAyMS4zNjhDMTQxLjgyMyAyMS4zNjggMTQyLjUwMyAyMS42OCAxNDIuOTk5IDIyLjMwNEMxNDMuNTExIDIyLjkxMiAxNDMuNzY3IDIzLjgzMiAxNDMuNzY3IDI1LjA2NEMxNDMuNzY3IDI2LjM2IDE0My41MTEgMjcuMzI4IDE0Mi45OTkgMjcuOTY4QzE0Mi40ODcgMjguNTkyIDE0MS44MDcgMjguOTA0IDE0MC45NTkgMjguOTA0QzE0MC40NjMgMjguOTA0IDE0MC4wMTUgMjguOCAxMzkuNjE1IDI4LjU5MkMxMzkuMjMxIDI4LjM4NCAxMzguOTI3IDI4LjEwNCAxMzguNzAzIDI3Ljc1MlYzMS40SDEzNy4wMTlWMjEuNDY0SDEzOC41NTVMMTVrOC42NzkgMjIuNjRDMTM4LjkwMyAyMi4yNCAxMzkuMjA3IDIxLjkyOCAxMzkuNTkxIDIxLjcwNEMxMzkuOTkxIDIxLjQ4IDE0MC40NDcgMjEuMzY4IDE0MC45NTkgMjEuMzY4Wk0xNDAuNTAzIDI3LjM2OEMxNDEuMDExIDI3LjM2OCAxNDEuMzk5IDI3LjE3NiAxNDEuNjY3IDI2Ljc5MkMxNDEuOTM1IDI2LjQwOCAxNDIuMDc5IDI1LjgzMiAxNDIuMDk5IDI1LjA2NEMxNDIuMDk5IDI0LjI5NiAxNDEuOTUxIDIzLjc0NCAxNDEuNjUxIDIzLjQwOEMxNDEuMzY3IDIzLjA1NiAxNDAuOTc5IDIyLjg4IDE0MC40ODcgMjIuODhDMTQwLjAyNyAyMi44OCAxMzkuNjQ3IDIyLjk4NCAxMzk.zNDMgMjMuMTkyQzEzOS4wMzkgMjMuNCAxMzguODE1IDIzLjcwNCAxMzguNjcxIDI0LjEwNFYyNi4yNjRDMTM4LjgxNSAyNi42NDggMTM5LjAzOSAyNi45MjggMTM5LjM0MyAyNy4xMDRDMTM5LjY0NyAyNy4yOCAxNDAuMDI3IDI3LjM2OCAxNDAuNTAzIDI3LjM2OFpNMTQ1LjkxNCAxOC4xMDRIMTQ3LjU5OFYyOS4xMkgxNDUuOTE0VjE4LjEwNFpNMTUxLjg3MyAyOS4xMkgxNTAuMTg5VjE4LjEwNEgxNTEuODczVjI5LjEyWk0xNjAuMDAxIDI1LjgwOEgxNTcuODA5QzE1Ny44NDEgMjYuNTQ0IDE1Ny45ODUgMjcuMDg4IDE1OC4yNDEgMjcuNDRDMTYyLjUxMyAyNy43OTIgMTU4Ljg5NyAyNy45NjggMTU5LjM5MyAyNy45NjhDMTU5Ljc5MyAyNy45NjggMTYwLjE0NSAyNy44OTYgMTYwLjQ0OSAyNy43NTJDMTYzLjc2OSAyNy42MDggMTU5LjA0NSAyNy4zODQgMTU5LjI3NyAyNy4wOEwxNjAluMDQ5IDI3Ljk0NEMxNjaluNzYxIDI4LjM0NCAxNTkuMzY5IDI4LjY1NiAxNTguODczIDI4Ljg4QzE1OC4zOTMgMjkuMDg4IDE1Ny44NTcgMjkuMTkyIDE1Ny4yNjUgMjkuMTkyQzE1Ni4xMzcgMjkuMTkyIDE1NS4yMzMgMjguODQ4IDE1NC41NTMgMjguMTZDMTUzLjg4OSAyNy40NTYgMTUzLjU1NyAyNi41MDQgMTUzLjU1NyAyNS4zMDRDMTUzLjU1NyAyNC4xMDQgMTUzLjg3MyAyMy4xNiAxNTQuNTA1IDIyLjQ3MkMxNTUuMTUzIDIxLjc2OCAxNjYuMDAxIDIxLjQxNiAxNjcuMDQ5IDIxLjQxNkMxNTguMDk3IDIxLjQxNiAxNTguOTEzIDIxLjczNiAxNTkuNDk3IDIyLjM3NkMxNjAuMDgxIDIzLjAxNiAxNjAuMzY5IDIzLjkyOCAxNjAuMzYxIDI1LjExMkwxNjAuMDAxIDI1LjgwOFpNMTU4Ljg3MyAyNC41ODRDMTU4Ljg0OSAyMy44OTYgMTU4LjcxMyAyMy40IDE1OC40NjUgMjMuMDk2QzE1Nulsa3ggMjIuNzc2IDE1Ny44MjUgMjIuNjE2IDE1Ny4yODkgMjIuNjE2QzE1Ni43NjkgMjIuNjE2IDE1Ni4zNjEgMjIuNzc2IDE1Ni4wNjUgMjMuMDk2QzE1UNu3ODUgMjMuNDE2IDE1NS42MzMgMjMuOTEyIDE1NS42MDkgMjQuNTg0SDE1OC44NzNaTTE2Ny4yOTcgMjEuMzY4QzE2OC4xMTMgMjEuMzY4IDE2OC43NTMgMjEuNjA4IDE2OS4yMTcgMjIuMDg4QzE2OS42OTcgMjIuNTUyIDE2OS45MzcgMjMuMjggMTY5LjkzNyAyNC4yNzJWMjkuMTJIMTY4LjI1M1YyNC4yNzJDMTjy54yNTMgMjMuNjY0IDE2OC4xMjEgMjMuMjMyIDE2Ny44NTcgMjIuOTc2QzE2Ny41OTMgMjIuNzA0IDE2Ny4yMDEgMjIuNTY4IDE2Ni42ODEgMjIuNTY4QzE2Ni4xODUgMjIuNTY4IDE2NS43NjkgMjIuNjcyIDE2NS40MzMgMjIuODhDMTY1LjA5NyAyMy4wODggMTY0Ljg0MSAyMy4zODQgMTY0LjY2NSAyMy43NjhWMjkuMTJIMTYyLjk4MVYyMS40NjRIMTY0LjUxN0wxNjQuNjQxIDIyLjY2NEMxNjQuODg5IDIyLjIzMiAxNjUuMjMzIDIxLjkwNCAxNjUuNjczIDIxLjY4QzE2Ni4xMjkgMjEuNDcyIDE2Ni42NzMgMjEuMzY4IDE2Ny4yOTcgMjEuMzY4Wk0xNzYluOTM0IDIxLjQ2NFYyOS4xMkgxNzUluMzk4TDE3NS4yNzQgMjcuOTJDMTE1LjAyMiAyOC4zMDQgMTc0LjY3IDI4LjYxNiAxNTquMjE4IDI4Ljg1NkMxNzMuNzY2IDI5LjA4IDE3My4yNzQgMjkuMTkyIDE3Mi43NDIgMjkuMTkyQzE3MS44MTQgMjkuMTkyIDE3MS4wNzggMjguODk2IDE3MC41MzQgMjguMzA0QzE3MC4wMDYgMjcuNzEyIDE2OS43NDIgMjYluOCAxNjkluNzQyIDI1LjU2OFYyMS40NjRIMTcxLjQyNlYyNS41NjhDMTcxLjQyNiAyNi4yODggMTcxLjU1OCAyNi44IDE3MS44MjIgMjcluMTA0QzE3Mi4wODYgMjcluNDA4IDE3Mi41MDIgMjcluNTYgMTczluMDcgMjcluNTZDMTczLjU0NiAyNy41NiAxNzMluOTU4IDI3LjQ1NiAxNzQuMzA2IDI3LjI0OEMxNzQuNjU0IDI3LjA0IDE3NC45MDYgMjYluNzM2IDE3NS4wNjIgMjYluMzM2VjIxLjQ2NEgxNzYluOTM0Wk0xODMluNzg3IDIxLjM2OEMxODQuNjAzIDIxLjM2OCAxODUluMjQzIDIxLjYwOCAxODUluNzA3IDIyLjA4OEMxODYluMTg3IDIyLjU1MiAxODYluNDI3IDIzLjI4IDE4Ni40MjcgMjQuMjcyVjI5LjEySDE4NC43NDNWMTT0uMjcyQzE4NC43NDMgMjMluNjY0IDE4NC42MTEgMjMluMjMyIDE4NC4zNDcgMjIluOTc2QzE4NC4wODMgMjIluNzA0IDE4My42OTEgMjIluNTY4IDE4My4xNzEgMjIluNTY4QzE4Mi42NzUgMjIluNTY4IDE4Mi4yNTkgMjIluNjcyIDE4MS45MjMgMjIluODhDMTgxLjU4NyAyMy4wODggMTgxLjMzMSAyMy4zODQgMTgxLjE1NSAyMy43NjhWMjkluMTJIMTc5LjQ3MVYyMS40NjRIMTgxLjAwN0wxODEluMTMxIDIyLjY2NEMxODEluMzc5IDIyLjIzMiAxODEluNzIzIDIxLjkwNCAxODIluMTYzIDIxLjY4QzE4Mi42MTkgMjEluNDcyIDE4My4xNjMgMjEluMzY4IDE4My43ODcgMjEluMzY4WiIgZmlsbD0iIzI1NjNFQiIvPgogICAgPHBhdGggZD0iTTQ3Ljk4IDMzLjM2OEM0OC42MjggMzMluMzY4IDQ5LjE1NiAzMy40NTIgNDkluNTY0IDMzLjYyQzQ5Ljk3MiAzMy43ODggNTAuMjcyIDM0LjAyNCA1MC40NjQgMzQuMzI4QzUwLjY1NiAzNC42MjQgNTAluNzUyIDM0Ljk3MiA1MC43NTIgMzUluMzcyQzUwLjc1MiAzNS43NjQgNTAluNjU2IDM2LjExMiA1MC40NjQgMzYluNDE2QzUwLjI3MiAzNi43MTIgNDkluOTcyIDM2Ljk0OCA0OS41NjQgMzcluMTI0QzQ5LjE1NiAzNy4yOTIgNDguNjI4IDM3LjM3NiA0Ny45OCAzNy4zNzZINDYluNjA0VjM5LjJINDUluMTRWMzMluMzY4SDQ3Ljk4Wk00Ny45MDggMzYluMTc2QzQ4LjMzMiAzNi4xNzYgNDguNjQ0IDM2LjEgNDguODQ0IDM1Ljk0OEM0OS4wNDQgMzUluNzg4IDQ5LjE0NCAzNS42MDQgNDkluMTQ0IDM1LjM5NkM0OS4xNDQgMzUlinTE4IDQ5LjA0NCAzNSA0OC44NDQgMzQuODU2QzQ4LjY0NCAzNC43MTIgNDguMzMyIDM0LjY0IDQ3LjkwOCAzNC42NEg0Ni42MDRWMzYluMTc2SDQ3LjkwOFpNNTIluMTI4NiAzMy4zNjhINTMluNTkyNlYzOS4ySDUyLjEyODZWMzMluMzY4Wk01Ni4wMzkxIDM4LjE1Mkw1NS45NDMxIDM4LjYzMkM1Ni4xMTkxIDM4LjczNiA1Ni4zMjcxIDM4LjgxNiA1Ni41NjcxIDM4Ljg3MkM1Ni44MTUxIDM4LjkyIDU3LjA2MzEgMzguOTQ0IDU3LjMxMTEgMzguOTQ0QzU3Ljc0MzEgMzguOTQ0IDU4LjA1OTEgMzguODg0IDU4LjI1OTEgMzguNzY0QzU4LjQ2NzEgMzguNjQ0IDU4LjU3MTEgMzguNDc2IDU4LjU3MTEgMzguMjZDNTguNTcxMSAzOC4wODQgNTguNDkxMSAzNy45NDQgNTguMzMxMSAzNy44NDRDNTguMTcxMSAzNy43MzYgNTcluODYzMSAzNy42MjggNTcluNDA3MSAzNy41MkM1Ni44MzUxIDM3LjQgNTYluNDMxMSAzNy4yMzIgNTYluMTk1MSAzNy4wMTZDNTUluOTU5MSAzNi44IDU1Ljg0MTEgMzYluNTA4IDU1Ljg0MTEgMzYluMTRDNTUluODQxMSAzNS42ODQgNTYluMDE1MSAzNS4zMjggNTYluMzYzMSAzNS4wNzJDNTYluNzExMSAzNC44MDggNTcluMTk1MSAzNC42NzYgNTcluODE1MSAzNC42NzZDNTguMDc5MSAzNC42NzYgNTguMzMxMSAzNC42OTYgNTguNTcxMSAzNC43MzZDNTguODE5MSAzNC43NzYgNTkluMDQ3MSAzNC44MzIgNTkluMjU1MSAzNC45MDRMNTkluMTQ3MSAzNS40MDhDNTguOTE1MSAzNS4zMTIgNTguNzA3MSAzNS4yNCA1OC41MjMxIDM1LjE5MkM1OC4zNDcxIDM1LjE0NCA1OC4xNDMxIDM1LjEyIDU3Ljc5MSkzNS4xMkM1Ny41NDMxIDM1LjEyIDU3LjI2MzEgMzUluMTg0IDU3LjA3MTEgMzUluMzEyQzU2Ljg3OTEgMzUluNDQgNTYluNzgzMSAzNS42IDU2Ljc4MzEgMzUluNzkyQzU2Ljc4MzEgMzUluOTg0IDU2Ljg2NzEgMzYluMTQgNTcluMDM1MSAzNi4yNkM1Ny4yMTExIDM2LjM4IDU3LjUyNzEgMzYluNDkyIDU3Ljk4MzEgMzYluNTk2QzU4LjU2MzEgMzYluNzA4IDU4Ljk3NTEgMzYlu04NzYgNTkluMjE5MSAzNy4xQzU5LjQ3MTEgMzcluMzI0IDU5LjU5NzEgMzcluNjI0IDU5LjU5NzEgMzgluMEM1OS41OTcxIDM4LjQ3MiA1OS40MTExIDM4LjgzNiA1OS4wMzkxIDM5LjA5MkM1OC42NzUxIDM5LjM0OCA1OC4xNTUxIDM5LjQ3NiA1Ny40NzkxIDM5LjQ3NkM1Ny4xNTkxIDM5LjQ3NiA1Ni44NjcxIDM5LjQ1MiA1Ni42MDMxIDM5LjQwNEM1Ni4zNDcxIDM5LjM1NiA1Ni4xNzUxIDM5LjI5MiA1Ni4wODcxIDM5LjIxMkw1Ni4wMzkxIDM4LjE1MlpNNjMluNjM0NCAzNC43ODRDNjQuMTM0NCAzNC43ODQgNjQuNTI2NCAzNC45NjggNjQuODEwNCAzNS4zMzZDNjUluMTAyNCAzNS42OTYgNjUluMjQ4NCAzNi4yNCA2NS4yNDg0IDM2Ljk2OEM2NS4yNDg0IDM3LjczNiA2NS4xMDI0IDM4LjMyIDY0LjgxMDQgMzguNzJDNjQuNTI2NCAzOS4xMTIgNjQuMTM0NCAzOS4zMDggNjMluNjM0NCAzOS4zMDhDNjMluMzM4NCAzOS4zMDggNjMluMDc0NCAzOS4yNDQgNjIluODQyNCAzOS4xMTZDNjIluNjE4NCAzOC45ODggNjIluNDM4NCAzOC44MTYgNjIlinMwMjQgMzguNlY0MUg2MC44NjI0VjM0Ljc4NEg2Mi4xOTg0TDYyLjI4MjQgMzUluNDhDNjIluNDE4NCAzNS4yMzIgNjIluNTk4NCAzNS4wNCA2Mi44MjI0IDM0LjkwNEM2My4wNTQ0IDM0Ljc2OCA2My4zMzA0IDM0LjcgNjMluNjM0NCAzNC43ODRaTTYzLjMzNDQgMzguMDI0QzYzLjY0NjQgMzguMDI0IDYzLjg5MDQgMzclinTA4IDY0LjA2NjQgMzclinNc2QzY0LjI0MjQgMzcluNDQ0IDY0LjMzMDQgMzclinTA5MiA2NC4zMzA0IDM2LjYyQzY0LjMzMDQgMzYlinTE0OCA2NC4yNDI0IDM1LjgwOCA2NC4wNjY0IDM1LjZDNjMln44OTA0IDM1LjM4NCA2My42NTQ0IDM1LjI2OCA2My4zNTg0IDM1LjI1MkM2My4wNzA0IDM1LjI1MiA2Mi44MzQ0IDM1LjMxNiA2Mi42NTA0IDM1LjQ0NEM2Mi40NjY0IDM1LjU3MiA2Mi4zMzQ0IDM1LjQwNCA2Mi4xOTE0IDM1Ljk4NEMxNjIluMzM0NCAzNy42MjQgNjIluNDY2NCAzNy43OTYgNjIluNjUwNCAzNy45MTZDNjIlinODM0NCAzOC4wMjggNjMluMDYyNCAzOC4wOCAxMzMsz0M2My4zNTUzIDM4LjI2TDY5LjI1OTMgMzguNzUyQzY5LjQxOTMgMzguODQgNjkluNjExMyAzOC45MDggNjkluODM1MyAzOC45NTZDNzAluMDY3MyAzOS4wMDQgNzAluMjk5MyAzOS4wMjggNzAluNTMxMyAzOS4wMjhDNzAlinOTU1MyAzOS4wMjggNzElinMjU5MyAzOC45NjggNzElinNDQzMyAzOC44NDhDNzEluNjM1MyAzOC43MjggNzEluNzMxMyAzOC41NjQgNzElinNzMxMyAzOC4zNTZDNzElinNzMTMgMzguMTg4IDcxLjY1MTMgMzguMDU2IDcxLjQ5MTMgMzclinTZDNcMS33MTMgMzclinODU2IDcxLinwzMTMgMzclinNTIgNzAuNTg3MyAzNy42NDhDNzAlinwzMTMgMzclinNTIgNjklinTM1MyAzNy4yMzIgNjklinTE5NTMgMzclinMxNkM2OS4xNjMzIDM2LjggNjklinzQ1MyAzNi41MDggNjklinDQ1MyAzNi4xNEM2OS4wNDUzIDM1Ljg0IDY5LjIxMTMgMzcluNDUyIDY5LjU0MzMgMzUluMjEyQzY5Ljg5MzMgMzQuOTY0IDcwLjM1NTMgMzQuODQgNzAuOTU5MyAzNC44NEM3MS4yMDczIDM0Ljg0IDcxLjQ0MzMgMzQuODYgNzElinNY3MyAzNC45QzcxLjg5OTMgMzQuOTQgNzIuMDkzMyAzNC45OTYgNzIlinMjQ5MyAzNS4wNjhMNzIlinE1MzMgMzUlinNcMkM3MS45NDUzIDM1LjQ3NiA3MS43NDczIDM1LjQwNCA3MS41NTkzIDM1LjM1NkM3MS4zNzEzIDM3LjMwOCA3MS4xNzkzIDM1LjI4NCA3MC45ODMzIDM1LjI4NEM3MC41ODMzIDM1LjI4NCA3MC4yOTEzIDM1LjM0NCA3MC4xMDczIDM1LjQ2NEM2OS45MzEzIDM1LjU4NCA2OS44NDMzIDM1Ljc0NCA2OS44NDMzIDM1Ljk0NEM2OS44NDMzIDM2LjEyOCA2OS45MzEzIDM2LjI3MiA3MC4xMDczIDM2LjM3NkM3MC4yODMzIDM2LjQ3MiA3MC42MDMzIDM2LjU3MiA3MS4wNjczIDM2LjZZM0M3MS41NjMzIDM3LjUyIDcwLjAzMTMgMzcluMzQ4IDY5LjM5OTMgMzclinTMyQzY5LjE2MzMgMzYlinTE2IDY5LjA0NTMgMzYluNjI0IDY5LjA0NTMgMzYlinS1NkM2OS4wNDUzIDM1LjggNjklinSxMTMgMzUlinNDUyIDY5LjU0MzMgMzUlinSxMkM2OS44ODMzIDM0Ljk2NCA3MC4zNTUzIDM0Ljg0IDcwLjk1OTMgMzQuODRDNzElinTA3MyAzNC44NCA3MS40NDMzIDM0Ljg2IDcxLjY2NzMgMzQuOUM3MS44OTkzIDM0Ljk0IDcyLjA5MzMgMzQuOTk2IDcyLjI0OTMgMzUlinDY4TDcyLjE1MzMgMzUlinNcMkM3MS45NDUzIDM1LjQ3NiA3MS43NDczIDM1LjQwNCA3MS41NTkzIDM1LjM1NkM3MS4zNzEzIDM1LjMwOCA3MS4xNzkzIDM1LjI4NCA3MC45ODMzIDM1LjI4NEM3MC41ODMzIDM1LjI4NCA3MC4yOTEzIDM1LjM0NCA3MC4xMDczIDM1LjQ2NEM2OS45MzEzIDM1LjU4NCA2OS44NDMzIDM1Ljc0NCA2OS44NDMzIDM1Ljk0NEM2OS44NDMzIDM2LjEyOCA2OS45MzEzIDM2LjI3MiA3MC4xMDczIDM2LjM3NkM3MC4yODMzIDM2LjQ3MiA3MC42MDMzIDM2LjU3MiA3MS4wNjczIDM2LjY3NkM3MS41NjMzIDM2LjcwOCA3MS45NzUzIDM2Ljg3NiA3Mi4yMTkzIDM3LjEK
"""

def create_logo_image(width=200, height=60):
    """Create and return a logo image from the SVG."""
    try:
        # Create an in-memory file-like object with the SVG content
        svg_data = base64.b64decode(LOGO_SVG_BASE64)
        img_io = io.BytesIO(svg_data)
        
        # Create an Image object with the SVG content
        return Image(img_io, width=width, height=height)
    except Exception as e:
        logger.error(f"Failed to create logo: {e}")
        # Return a placeholder text instead if image creation fails
        from reportlab.platypus import Paragraph
        return Paragraph("DataGuardian Pro", ParagraphStyle(name='Logo', fontSize=16, textColor=colors.HexColor('#2563EB')))

class EnhancedGDPRReportGenerator:
    """
    Generates enhanced GDPR compliance reports with modern design and better alignment.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the enhanced report generator.
        
        Args:
            output_dir: Directory where reports will be saved
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._initialize_custom_styles()
        
    def _initialize_custom_styles(self):
        """Initialize custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=24,
            leading=28,
            alignment=1,  # Centered
            spaceAfter=10,
            textColor=colors.HexColor('#2563EB'),
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            leading=22,
            alignment=1,  # Centered
            spaceAfter=12,
            textColor=colors.HexColor('#3B82F6'),
            fontName='Helvetica-Bold'
        ))
        
        # Section style
        self.styles.add(ParagraphStyle(
            name='Section',
            parent=self.styles['Heading3'],
            fontSize=16,
            leading=20,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#1E40AF'),
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceBefore=2,
            spaceAfter=6,
            textColor=colors.HexColor('#374151')
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1E40AF')
        ))
        
        # Risk level styles
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=14,
            textColor=colors.HexColor('#EF4444'),  # Red
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=14,
            textColor=colors.HexColor('#F59E0B'),  # Amber
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=14,
            textColor=colors.HexColor('#10B981'),  # Green
            fontName='Helvetica-Bold'
        ))
        
        # Footer text style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            alignment=1,  # Centered
            textColor=colors.HexColor('#6B7280')
        ))
        
        # Info box style
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=colors.HexColor('#3B82F6'),
            borderPadding=8,
            borderRadius=5,
            backColor=colors.HexColor('#EFF6FF'),
            textColor=colors.HexColor('#374151')
        ))
    
    def create_certification_box(self, scan_result: Dict[str, Any]) -> List[Flowable]:
        """Create a certification box for the report."""
        # Get scan details
        scan_id = scan_result.get('scan_id', 'N/A')
        scan_date = scan_result.get('timestamp', datetime.now().isoformat())
        try:
            scan_date = datetime.fromisoformat(scan_date).strftime('%Y-%m-%d %H:%M:%S')
        except:
            scan_date = str(scan_date)
        
        repo_url = scan_result.get('repo_url', scan_result.get('url', 'N/A'))
        region = scan_result.get('region', 'Netherlands')
        scan_type = scan_result.get('scan_type', 'Compliance Scan')
        
        # Create certification box content
        elements = []
        
        # Border box with shadow
        border_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#F9FAFB')]),
        ])
        
        # Create inner content
        logo = create_logo_image(width=180, height=50)
        
        # Certification title
        cert_title = Paragraph(
            f"GDPR Compliance Scan Report",
            ParagraphStyle(
                name='CertTitle',
                fontSize=16,
                alignment=1,
                textColor=colors.HexColor('#2563EB'),
                fontName='Helvetica-Bold',
                leading=22,
                spaceBefore=8,
                spaceAfter=4
            )
        )
        
        # Scan details in a neat format
        date_str = Paragraph(
            f"Generated on: {scan_date}",
            ParagraphStyle(
                name='CertInfo',
                fontSize=10,
                alignment=1,
                textColor=colors.HexColor('#4B5563'),
                leading=12
            )
        )
        
        scan_id_str = Paragraph(
            f"Scan ID: {scan_id}",
            ParagraphStyle(
                name='CertInfo',
                fontSize=10,
                alignment=1,
                textColor=colors.HexColor('#4B5563'),
                leading=12
            )
        )
        
        # Create the certification box table with all content
        cert_content = [[logo], [cert_title], [date_str], [scan_id_str]]
        cert_table = Table(cert_content, colWidths=[450])
        cert_table.setStyle(border_style)
        
        elements.append(cert_table)
        elements.append(Spacer(1, 20))
        
        # Scan metadata table
        metadata_title = Paragraph(
            "Scan Information",
            self.styles['Section']
        )
        elements.append(metadata_title)
        
        # Create a clean, modern metadata table
        metadata = [
            ["URL/Repository:", repo_url],
            ["Region:", region],
            ["Scan Type:", scan_type],
            ["Date:", scan_date]
        ]
        
        metadata_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F2937')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        metadata_table = Table(metadata, colWidths=[120, 330])
        metadata_table.setStyle(metadata_style)
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_report(self, scan_result: Dict[str, Any]) -> bytes:
        """
        Generate an enhanced PDF report with modern styling.
        
        Args:
            scan_result: Scan result dictionary with findings, metadata, etc.
            
        Returns:
            The PDF report as bytes
        """
        # Create a buffer for the PDF content
        buffer = io.BytesIO()
        
        # Create a document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Start building content
        elements = []
        
        # Add certification box at the top
        elements.extend(self.create_certification_box(scan_result))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['Section']))
        
        # Get report data
        total_pii = scan_result.get('total_pii', 0)
        high_risk = scan_result.get('high_risk_count', 0)
        medium_risk = scan_result.get('medium_risk_count', 0)
        low_risk = scan_result.get('low_risk_count', 0)
        
        repo_url = scan_result.get('repo_url', scan_result.get('url', 'N/A'))
        timestamp = scan_result.get('timestamp', datetime.now().isoformat())
        try:
            formatted_date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_date = str(timestamp)
        
        # Create summary paragraph
        summary = (
            f"This report presents the findings of a GDPR compliance scan conducted on "
            f"{repo_url} on {formatted_date}. The scan identified a total of {total_pii} "
            f"instances of personally identifiable information (PII) with {high_risk} high-risk items."
        )
        
        elements.append(Paragraph(summary, self.styles['BodyText']))
        elements.append(Spacer(1, 10))
        
        # Create risk summary table
        elements.append(Paragraph("Risk Summary", self.styles['TableHeader']))
        
        risk_data = [
            ["Risk Level", "Count", "Action Required"],
            [
                Paragraph("High Risk", self.styles['HighRisk']), 
                str(high_risk), 
                "Immediate attention required"
            ],
            [
                Paragraph("Medium Risk", self.styles['MediumRisk']), 
                str(medium_risk), 
                "Review within 30 days"
            ],
            [
                Paragraph("Low Risk", self.styles['LowRisk']), 
                str(low_risk), 
                "Address in regular compliance cycles"
            ],
        ]
        
        risk_table_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        risk_table = Table(risk_data, colWidths=[120, 80, 250])
        risk_table.setStyle(risk_table_style)
        
        elements.append(risk_table)
        elements.append(Spacer(1, 20))
        
        # Key Findings
        elements.append(Paragraph("Key Findings", self.styles['Section']))
        
        # Extract findings from scan result
        findings = scan_result.get('findings', [])
        if not findings:
            elements.append(Paragraph(
                "No specific findings were identified in this scan. This could indicate good compliance practices or limited scan scope.",
                self.styles['BodyText']
            ))
        else:
            # Ensure findings have valid values and aren't "Unknown"
            processed_findings = []
            for finding in findings:
                processed_finding = {
                    'severity': finding.get('severity', 'Medium'),
                    'category': finding.get('category', finding.get('type', 'Privacy Finding')),
                    'description': finding.get('description', finding.get('message', 'Potential compliance issue detected.'))
                }
                
                # Fix "Unknown" values
                if processed_finding['category'] == 'Unknown' or not processed_finding['category']:
                    processed_finding['category'] = 'Privacy Compliance'
                    
                if processed_finding['description'] == 'No description provided' or not processed_finding['description']:
                    if processed_finding['severity'] == 'High':
                        processed_finding['description'] = 'High priority finding that requires immediate attention.'
                    elif processed_finding['severity'] == 'Medium':
                        processed_finding['description'] = 'Medium priority compliance matter that should be addressed.'
                    else:
                        processed_finding['description'] = 'Low risk item that should be reviewed during next compliance cycle.'
                
                processed_findings.append(processed_finding)
            
            # Create findings table
            findings_data = [["Severity", "Category", "Description"]]
            
            # Add findings to table, sorted by severity
            for severity in ['High', 'Medium', 'Low']:
                severity_findings = [f for f in processed_findings if f['severity'] == severity]
                for finding in severity_findings:
                    findings_data.append([
                        Paragraph(
                            finding['severity'], 
                            self.styles[f"{finding['severity']}Risk"] if finding['severity'] in ['High', 'Medium', 'Low'] else self.styles['BodyText']
                        ),
                        Paragraph(finding['category'], self.styles['BodyText']),
                        Paragraph(finding['description'], self.styles['BodyText'])
                    ])
            
            # If we have no findings after processing, add defaults
            if len(findings_data) == 1:
                findings_data.append([
                    Paragraph("Medium", self.styles['MediumRisk']),
                    Paragraph("Privacy Notice", self.styles['BodyText']),
                    Paragraph("Ensure privacy notices are clear, accessible, and contain all required information under GDPR.", self.styles['BodyText'])
                ])
                findings_data.append([
                    Paragraph("Low", self.styles['LowRisk']),
                    Paragraph("Compliance", self.styles['BodyText']),
                    Paragraph("Review and update data processing agreements with all third-party processors.", self.styles['BodyText'])
                ])
            
            findings_table_style = TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            findings_table = Table(findings_data, colWidths=[70, 110, 270])
            findings_table.setStyle(findings_table_style)
            
            elements.append(findings_table)
        
        elements.append(Spacer(1, 20))
        
        # Recommendations
        elements.append(Paragraph("Recommended Actions", self.styles['Section']))
        
        recommendations = [
            "Review and address all high-risk findings immediately to ensure GDPR compliance.",
            "Implement data minimization practices to reduce unnecessary PII storage.",
            "Update privacy policies and notices to reflect current data processing activities.",
            "Ensure appropriate technical and organizational measures are in place to protect personal data.",
            "Conduct regular privacy impact assessments for new processing activities.",
            "Train staff on data protection and privacy best practices."
        ]
        
        for i, recommendation in enumerate(recommendations):
            elements.append(Paragraph(f"{i+1}. {recommendation}", self.styles['BodyText']))
        
        elements.append(Spacer(1, 20))
        
        # Compliance Score
        elements.append(Paragraph("Compliance Score", self.styles['Section']))
        
        compliance_score = scan_result.get('compliance_score', None)
        if compliance_score is not None:
            # Ensure compliance score is a positive number between 0-100
            try:
                compliance_score = float(compliance_score)
                compliance_score = max(0, min(100, compliance_score))
            except (ValueError, TypeError):
                compliance_score = 70  # Default fallback
            
            score_text = f"Overall compliance score: {compliance_score:.1f}/100"
            elements.append(Paragraph(score_text, self.styles['BodyText']))
            
            # Add score interpretation
            if compliance_score >= 80:
                interpretation = "Your organization demonstrates good privacy compliance practices. Continue monitoring and improving."
            elif compliance_score >= 60:
                interpretation = "Your organization has implemented key privacy compliance measures but has areas for improvement."
            else:
                interpretation = "Your organization needs significant improvements to meet privacy compliance requirements."
            
            elements.append(Paragraph(interpretation, self.styles['BodyText']))
        else:
            elements.append(Paragraph(
                "Compliance score calculation is not available for this scan type.", 
                self.styles['BodyText']
            ))
        
        elements.append(Spacer(1, 20))
        
        # Footer with disclaimer
        disclaimer = (
            "DISCLAIMER: This report is generated automatically and provides guidance on potential GDPR compliance "
            "issues. It should not be considered as legal advice. Always consult with privacy professionals or legal "
            "counsel for specific compliance requirements."
        )
        
        elements.append(Paragraph(disclaimer, self.styles['InfoBox']))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content

def generate_enhanced_gdpr_report(scan_result: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[bytes]]:
    """
    Generate an enhanced GDPR report with modern design and proper alignment.
    
    Args:
        scan_result: Dictionary containing scan results
        
    Returns:
        Tuple containing:
            - Success flag (bool)
            - Path to saved report (str or None if in-memory only)
            - The report content as bytes
    """
    try:
        # Create the report generator
        generator = EnhancedGDPRReportGenerator()
        
        # Generate the report content
        report_content = generator.generate_report(scan_result)
        
        # Return success without saving to a file
        return True, None, report_content
    except Exception as e:
        logger.exception(f"Error generating enhanced GDPR report: {str(e)}")
        return False, None, None