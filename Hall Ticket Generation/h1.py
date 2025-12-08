"""
Hall Ticket Generator (PDF only)

Generates PDF hall tickets for mock participants (no QR in PDF).

Usage (Windows cmd):
  1) Install deps:
	 pip install reportlab
  2) Run:
	 python "Hall Ticket Generation\\h1.py"

Outputs PDF files under ./Hall Ticket Generation/output/
"""

import os
from datetime import datetime
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph


# --------------------------
# Configuration
# --------------------------
EVENT_NAME = "One-Stop Hackathon"
EVENT_DATE = "Dec 14–15, 2025"
EVENT_VENUE = "Tech Convention Center, Bengaluru"
ORG_NAME = "Hackathon Committee"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def ensure_output_dir() -> str:
	os.makedirs(OUTPUT_DIR, exist_ok=True)
	return OUTPUT_DIR


def make_mock_participants(n: int = 10) -> List[Dict]:
	"""Create mock participant data."""
	tracks = ["AI/ML", "Web", "Mobile", "Data", "IoT"]
	colleges = [
		"Tech Institute of India",
		"Global Engineering College",
		"City University",
		"National Institute of Technology",
		"Regional College of Engineering",
	]
	participants: List[Dict] = []
	for i in range(1, n + 1):
		reg_id = f"HACK-{datetime.now().strftime('%Y%m%d')}-{i:03d}"
		participants.append(
			{
				"name": f"Participant {i}",
				"college": colleges[i % len(colleges)],
				"email": f"participant{i}@example.com",
				"phone": f"9{str(100000000 + i).zfill(9)}",
				"track": tracks[i % len(tracks)],
				"reg_id": reg_id,
				"team": f"Team-{(i-1)//3 + 1}",
			}
		)
	return participants




def draw_header(c: canvas.Canvas, width: float, height: float):
	c.setFillColor(colors.black)
	c.setFont("Helvetica-Bold", 18)
	c.drawString(20 * mm, height - 25 * mm, EVENT_NAME)
	c.setFont("Helvetica", 12)
	c.drawString(20 * mm, height - 32 * mm, f"Organized by {ORG_NAME}")
	c.drawString(20 * mm, height - 39 * mm, f"Venue: {EVENT_VENUE}")
	c.drawString(20 * mm, height - 46 * mm, f"Date: {EVENT_DATE}")
	# Decorative line
	c.setStrokeColor(colors.HexColor("#333333"))
	c.setLineWidth(1)
	c.line(20 * mm, height - 50 * mm, width - 20 * mm, height - 50 * mm)


def draw_footer(c: canvas.Canvas, width: float):
	c.setFont("Helvetica", 9)
	c.setFillColor(colors.HexColor("#666666"))
	c.drawString(20 * mm, 15 * mm, "Please carry a valid ID card. QR code required for entry.")
	c.drawRightString(width - 20 * mm, 15 * mm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


def render_hall_ticket(p: Dict, out_path: str):
	"""Render a single PDF hall ticket for participant p."""
	width, height = A4
	c = canvas.Canvas(out_path, pagesize=A4)

	# Header
	draw_header(c, width, height)

	# Participant block
	c.setFont("Helvetica-Bold", 14)
	c.drawString(20 * mm, height - 70 * mm, "Hall Ticket")

	c.setFont("Helvetica", 12)
	y = height - 85 * mm
	line_gap = 8 * mm
	fields = [
		("Name", p["name"]),
		("Registration ID", p["reg_id"]),
		("Track", p["track"]),
		("Team", p["team"]),
		("College", p["college"]),
		("Email", p["email"]),
		("Phone", p["phone"]),
	]
	for label, value in fields:
		c.setFont("Helvetica-Bold", 11)
		c.drawString(20 * mm, y, f"{label}:")
		c.setFont("Helvetica", 11)
		c.drawString(55 * mm, y, value)
		y -= line_gap

	# No QR on the hall ticket; portal will display QR separately for download

	# Instruction paragraph
	styles = getSampleStyleSheet()
	style = styles["Normal"]
	style.fontName = "Helvetica"
	style.fontSize = 10
	style.leading = 13
	
	

	# Footer
	draw_footer(c, width)

	c.showPage()
	c.save()


def generate_all(n: int = 1) -> List[str]:
	ensure_output_dir()
	participants = make_mock_participants(n)
	out_files: List[str] = []
	for p in participants:
		filename = f"{p['reg_id']}_{p['name'].replace(' ', '_')}.pdf"
		out_path = os.path.join(OUTPUT_DIR, filename)
		render_hall_ticket(p, out_path)
		out_files.append(out_path)
	return out_files


def main():
	print("Generating hall tickets with QR codes...")
	out_files = generate_all(n=1)
	print(f"Done. Generated {len(out_files)} files in: {OUTPUT_DIR}")
	for f in out_files[:3]:
		print(" -", f)


if __name__ == "__main__":
	main()
