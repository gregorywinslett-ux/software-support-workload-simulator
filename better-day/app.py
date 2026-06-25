from __future__ import annotations

import base64
from collections import Counter
from copy import deepcopy
from html import escape
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
HERO_IMAGE = APP_DIR / "assets" / "workday-cockpit-hero.png"


st.set_page_config(
    page_title="Better Day",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


TEAMS = [
    "ITaLI Academic Group",
    "Analysis - Technology and Pedagogy",
    "Business Services",
    "Educational Media Production",
    "eLearning Systems and Support",
    "Learning Design",
    "Professional Learning and Recognition",
    "Student Surveys and Evaluations",
    "UQx",
]

ROLE_POSTURES = [
    "Team member",
    "Team lead",
    "Specialist adviser",
    "Project contributor",
    "Cross-team collaborator",
]

CLIMATE_START = {
    "Psychological safety": 56,
    "Workload pressure": 54,
    "Inclusion climate": 55,
    "Role clarity": 53,
    "Team trust": 57,
}

SYSTEM_PRESSURE_START = {
    "Urgency": 58,
    "Ambiguity": 54,
    "Visibility to senior stakeholders": 42,
    "Cross-team dependency": 48,
    "Emotional load": 46,
}

TEAM_PROFILES = {
    "ITaLI Academic Group": {
        "purpose": "Partners with academics, educational leaders, professional staff and students to enhance teaching, curriculum and assessment practice through evidence-informed educational leadership.",
        "stakeholders": ["academics", "program leaders", "course leaders", "learning designers", "faculty teaching and learning committees", "university leadership", "students"],
        "pressures": ["evidence-informed advice under time pressure", "strategic ambiguity", "high expectations", "policy sensitivity", "balancing expertise with collegiality"],
        "positive_behaviours": ["name uncertainty", "invite local context", "translate evidence into practical choices", "avoid expert overreach", "recognise academic judgement"],
        "requests": ["A faculty committee asks for rapid advice on an assessment redesign with several unresolved constraints.", "A course leader wants a firm answer before the evidence and local context are clear."],
        "debrief": "Your day asked you to balance educational leadership with humility, practical judgement and care for local context.",
    },
    "Analysis - Technology and Pedagogy": {
        "purpose": "Guides the design, selection and adoption of educational technologies that are pedagogically sound and aligned with teaching goals.",
        "stakeholders": ["course coordinators", "tutors", "students", "learning designers", "eLearning systems staff", "ITS", "Library", "AskUS"],
        "pressures": ["emerging technologies", "unclear requirements", "UI/UX concerns", "governance", "security", "accessibility", "excitement outpacing readiness"],
        "positive_behaviours": ["clarify the educational purpose", "ask constructive questions", "surface risks without blocking innovation", "translate between technical and pedagogical language"],
        "requests": ["A course team wants to pilot a new tool next week, but the teaching purpose is still fuzzy.", "A colleague asks whether a new platform is approved before security and accessibility questions have been worked through."],
        "debrief": "Your day centred on translating between pedagogical ambition, technical reality and responsible adoption.",
    },
    "Business Services": {
        "purpose": "Supports the smooth running of ITaLI operations, communications, events, finance, facilities, HR coordination and business processes.",
        "stakeholders": ["ITaLI teams", "P&F", "HR", "FBS", "ITS", "M&C", "ODVCA"],
        "pressures": ["invisible operational labour", "urgent requests", "competing team needs", "events", "procurement", "space", "safety", "unclear priority"],
        "positive_behaviours": ["make constraints visible", "prioritise transparently", "protect respectful service boundaries", "explain process constructively", "recognise hidden work"],
        "requests": ["Three teams ask for urgent operational support at the same time, each assuming their request is quick.", "An event request arrives late with finance, room and communications dependencies."],
        "debrief": "Your day highlighted the importance of making hidden operational work visible while staying constructive and service-minded.",
    },
    "Educational Media Production": {
        "purpose": "Develops high-quality media solutions that enhance teaching materials and student learning.",
        "stakeholders": ["students", "academics", "school and faculty learning design teams", "ITaLI and ODVCA staff", "external partners"],
        "pressures": ["production timelines", "creative expectations", "unclear scope", "quality standards", "accessibility", "brand alignment"],
        "positive_behaviours": ["clarify scope early", "negotiate quality and time trade-offs", "protect creative labour", "communicate production constraints respectfully"],
        "requests": ["An academic asks for a polished video by Friday, but the brief is still changing.", "A partner wants an extra media format added after production has already started."],
        "debrief": "Your day asked you to protect creative quality and sustainable production while keeping learning outcomes in view.",
    },
    "eLearning Systems and Support": {
        "purpose": "Maintains reliable operation of central online-learning systems and supports teaching staff to use digital learning effectively.",
        "stakeholders": ["teaching staff", "learning designers", "ITS", "Library", "examinations", "DVCA Office", "vendors", "faculties"],
        "pressures": ["urgent support requests", "system reliability", "assessment pressure", "frustrated users", "vendor dependencies", "service volume"],
        "positive_behaviours": ["respond calmly under pressure", "clarify what is known and unknown", "avoid blame", "communicate next steps", "protect sustainable support boundaries"],
        "requests": ["A frustrated teaching team reports an issue during an assessment window and wants an immediate answer.", "A vendor dependency blocks a fix while staff keep asking for certainty."],
        "debrief": "Your day tested calm communication, service boundaries and clarity when system pressure was high.",
    },
    "Learning Design": {
        "purpose": "Supports and champions UQ's teaching community through evidence-informed design, co-design, consultation, professional development and strategic initiatives.",
        "stakeholders": ["academics", "teaching leaders", "students", "ITaLI teams", "DVCA portfolio teams", "faculty and school learning designers"],
        "pressures": ["hidden workload", "ambiguous requests", "academic autonomy", "strategic priority overload", "cross-team dependencies", "co-design complexity"],
        "positive_behaviours": ["clarify the real design problem", "co-design rather than rescue", "invite student and accessibility perspectives", "make workload visible", "connect strategy to practical action"],
        "requests": ["A course team asks you to quickly redesign an assessment, but the real design problem is still unclear.", "A strategic project needs learning design input without recognising the hidden workload already committed."],
        "debrief": "Your day asked you to turn ambiguity into co-designed action without absorbing every unresolved problem yourself.",
    },
    "Professional Learning and Recognition": {
        "purpose": "Fosters teaching excellence by delivering professional learning, recognition pathways, awards, grants, fellowships and teaching development programs.",
        "stakeholders": ["UQ teaching and learning community", "applicants", "fellows", "award nominees", "teaching leaders", "program participants"],
        "pressures": ["high expectations", "disappointment", "quality assurance", "recognition processes", "developmental feedback", "event/program delivery"],
        "positive_behaviours": ["give honest feedback with care", "preserve dignity", "clarify pathways", "recognise effort", "support growth without overpromising"],
        "requests": ["An applicant asks for reassurance about an outcome you cannot promise.", "A program participant wants quick feedback before the quality process is complete."],
        "debrief": "Your day focused on honest developmental support, dignity and transparent pathways.",
    },
    "Student Surveys and Evaluations": {
        "purpose": "Manages academic-quality systems for student feedback on courses and teaching, supporting quality assurance and evidence-based improvement.",
        "stakeholders": ["academic staff", "professional staff", "schools", "faculties", "system owners", "DVCA Office", "PBI", "ITS", "accreditation bodies"],
        "pressures": ["policy compliance", "data integrity", "survey timing", "stakeholder pressure", "requests for exceptions", "complex reporting"],
        "positive_behaviours": ["maintain fairness", "explain rationale clearly", "protect data integrity", "support evidence-based improvement", "distinguish what is possible from what is appropriate"],
        "requests": ["A school asks for an exception that would make reporting easier but could affect fairness.", "A stakeholder wants a fast data cut before the context and caveats are clear."],
        "debrief": "Your day highlighted fairness, data integrity and clear rationale under stakeholder pressure.",
    },
    "UQx": {
        "purpose": "Creates extramural and micro-credential learning environments and modules for large-scale diverse learners.",
        "stakeholders": ["teaching and learning leaders", "DTLs", "ADAs", "teaching academics", "ITaLI teams", "PVC portfolios", "Library", "DVCA staff", "external learners"],
        "pressures": ["scale", "learner diversity", "partner expectations", "digital pedagogy", "production timelines", "platform constraints"],
        "positive_behaviours": ["clarify audience and purpose", "design for diverse learners", "negotiate sustainable scope", "connect quality with scale", "make assumptions visible"],
        "requests": ["A partner wants to expand a module for a broad learner group without revisiting assumptions about audience needs.", "A micro-credential timeline tightens while quality expectations stay the same."],
        "debrief": "Your day asked you to connect quality, scale and learner diversity while negotiating sustainable scope.",
    },
}

ROLE_LENSES = {
    "Team member": "You are close to the practical work and can make impact by making work visible early.",
    "Team lead": "Your leadership signals shape whether people feel able to name pressure, ambiguity and missing voices.",
    "Specialist adviser": "Your expertise helps, especially when it is paired with curiosity, limits and practical translation.",
    "Project contributor": "You influence the day through clear dependencies, realistic commitments and respectful follow-through.",
    "Cross-team collaborator": "You help the system work better by translating needs and connecting people before assumptions harden.",
}

TAG_TO_PROFILE = {
    "clarifying ownership": "The Clarifier",
    "making workload visible": "The Boundary Setter",
    "inviting missing voices": "The Inclusion Builder",
    "respectful boundary-setting": "The Boundary Setter",
    "calm under pressure": "The Practical Advocate",
    "checking assumptions": "The Clarifier",
    "naming trade-offs": "The Practical Advocate",
    "repairing misunderstanding": "The Repairer",
    "escalating appropriately": "The Practical Advocate",
    "connecting to shared purpose": "The Connector",
    "preserving dignity": "The Inclusion Builder",
    "co-design rather than rescue": "The Connector",
    "translating complexity": "The Practical Advocate",
    "recognising hidden work": "The Inclusion Builder",
    "explaining rationale": "The Clarifier",
}

PROFILE_DETAILS = {
    "The Clarifier": {
        "description": "Makes ownership, expectations and next steps visible.",
        "contributes": "Reduces ambiguity and hidden work by making ownership, timelines and decision rights visible.",
        "overused": "Can feel like delay or process if it is not paired with warmth and purpose.",
        "inclusive": "Helps people participate because they can see what is being decided and what information matters.",
        "practice": "Before moving to action, ask what decision is needed, who owns it and what evidence is missing.",
        "systemic": "Where do decision rights need to be clearer?",
    },
    "The Connector": {
        "description": "Brings people, perspectives and dependencies together.",
        "contributes": "Makes dependencies and shared purpose visible across roles or teams.",
        "overused": "Can become a personal coordination burden if the system relies on you to hold every relationship.",
        "inclusive": "Reduces late surprises by inviting the right perspectives before decisions harden.",
        "practice": "Name one dependency and invite the right person into the conversation before solution mode.",
        "systemic": "Which dependencies need clearer handover routines?",
    },
    "The Boundary Setter": {
        "description": "Protects sustainable work without withdrawing support.",
        "contributes": "Protects sustainable work by turning workload pressure into a discussable trade-off.",
        "overused": "Can feel distant if the boundary is not explained through purpose, fairness or quality.",
        "inclusive": "Helps hidden labour become visible before it falls unevenly on quieter or more responsive people.",
        "practice": "When pressure rises, name the trade-off and ask what should pause or change.",
        "systemic": "Where is work being absorbed rather than prioritised?",
    },
    "The Repairer": {
        "description": "Notices relational impact and restores trust.",
        "contributes": "Keeps work discussable after tension, ambiguity or unintended impact.",
        "overused": "Can become over-personalised if every systems pressure is treated as an interpersonal mistake.",
        "inclusive": "Preserves dignity and makes it easier for people to re-enter a conversation.",
        "practice": "Use one repair sentence tomorrow: 'I want to pause because I may have moved too quickly there.'",
        "systemic": "What system pressure made the repair necessary?",
    },
    "The Inclusion Builder": {
        "description": "Creates space for quieter, newer or less powerful voices.",
        "contributes": "Surfaces risks, constraints and experience that may otherwise arrive too late.",
        "overused": "Can broaden the conversation without improving the decision unless ownership and next steps are clear.",
        "inclusive": "Changes the process so contribution is easier and less dependent on confidence or status.",
        "practice": "Before a decision lands, ask whose experience or constraint has not been heard yet.",
        "systemic": "Which voices are heard late, only after decisions are mostly formed?",
    },
    "The Practical Advocate": {
        "description": "Turns values and constraints into workable action.",
        "contributes": "Turns complexity into workable next steps while keeping constraints visible.",
        "overused": "Can become over-accommodation if moving forward hides the real cost of the work.",
        "inclusive": "Makes action possible without pretending trade-offs have disappeared.",
        "practice": "Frame the next step as a realistic option with visible constraints and a clear owner.",
        "systemic": "What do we need to stop, pause or sequence differently?",
    },
}


# Scenario maturity rules:
# 1. No cartoon villains.
# 2. No perfect choices.
# 3. Every choice must help something and risk something.
# 4. Consequences should include what remains unresolved.
# 5. Stakeholder reactions should be mixed and realistic.
# 6. Repair is always possible.
# 7. Individual behaviours are framed within broader systems of work.


def option(
    label,
    action,
    helps,
    risk,
    unresolved,
    tags,
    effects,
    system_effects=None,
    reaction="",
    delayed_consequence=None,
    repair=False,
):
    return {
        "label": label,
        "action": action,
        "helps": helps,
        "risk": risk,
        "unresolved": unresolved,
        "tags": tags,
        "effects": effects,
        "system_effects": system_effects or {},
        "reaction": reaction,
        "delayed_consequence": delayed_consequence,
        "repair": repair,
    }


def build_scenes(team: str, role: str) -> list[dict]:
    profile = TEAM_PROFILES[team]
    stakeholder = profile["stakeholders"][0]
    second_stakeholder = profile["stakeholders"][1]
    third_stakeholder = profile["stakeholders"][2] if len(profile["stakeholders"]) > 2 else "a colleague"
    pressure = profile["pressures"][0]
    request = profile["requests"][0]
    role_lens = ROLE_LENSES[role]
    behaviour = profile["positive_behaviours"][0]

    return [
        {
            "time": "8:45 am",
            "title": "Start-of-day scan",
            "narrative": f"You open the day in {team}. {role_lens} The calendar already shows a handover, a meeting with {second_stakeholder}, and one request linked to {pressure}.",
            "situation": f"A message from {stakeholder} asks whether you can 'quickly look over something' before lunch. It may be small, or it may be the edge of a larger piece of work.",
            "options": [
                option(
                    "Clarify before committing",
                    "Ask what decision is needed, what deadline matters most, and what could pause if this becomes urgent.",
                    "Makes the work visible before responsibility is silently absorbed.",
                    "May feel slower in a moment where the requester wants immediate reassurance.",
                    "The deadline may still be unrealistic unless someone makes a priority decision.",
                    ["clarifying ownership", "making workload visible", "respectful boundary-setting"],
                    {"Role clarity": 8, "Team trust": 3, "Psychological safety": 2, "Workload pressure": -3},
                    {"Ambiguity": -8, "Urgency": 2, "Emotional load": -2},
                    f"The {stakeholder} accepts the clarification and gives more context, though they still need help deciding what can wait.",
                    {
                        "trigger_scene": 3,
                        "text": "Your earlier clarification creates a useful pattern. A colleague names the decision owner and deadline before asking for help.",
                        "effects": {"Role clarity": 5, "Workload pressure": -3, "Psychological safety": 2},
                        "system_effects": {"Ambiguity": -5, "Emotional load": -2},
                        "reaction": "The request is more workable, although the wider priority queue is still crowded.",
                        "tags": ["clarifying ownership", "making workload visible"],
                    },
                ),
                option(
                    "Help quickly and keep moving",
                    "Say yes, do a first pass, and plan to fit the extra work between existing commitments.",
                    "Builds goodwill and gives the requester something useful quickly.",
                    "Reinforces the pattern that urgent work travels to whoever responds fastest.",
                    "Ownership, scope and what should move down the list remain unclear.",
                    ["calm under pressure", "translating complexity"],
                    {"Team trust": 3, "Workload pressure": 7, "Role clarity": -4},
                    {"Urgency": 5, "Ambiguity": 3, "Emotional load": 4},
                    f"The {stakeholder} seems relieved, but the response also makes you the easiest path for the next question.",
                    {
                        "trigger_scene": 4,
                        "text": "Because you accepted the earlier request without clarifying ownership, two more questions now come directly to you. People trust you to help, but the work is becoming less visible.",
                        "effects": {"Team trust": 2, "Workload pressure": 8, "Role clarity": -5},
                        "system_effects": {"Urgency": 4, "Ambiguity": 4, "Emotional load": 4},
                        "reaction": "The requests are polite, but the system is routing pressure toward the person who responded fastest.",
                        "tags": ["calm under pressure"],
                    },
                    True,
                ),
                option(
                    "Redirect to the pathway",
                    "Point them to the usual process and say you can advise once the request is clearer.",
                    "Protects capacity and keeps the process from being bypassed.",
                    "Can feel procedural if the reason for the boundary is not explained.",
                    "The requester may still not know how to frame the work or who owns the decision.",
                    ["respectful boundary-setting", "explaining rationale"],
                    {"Workload pressure": -4, "Role clarity": 2, "Psychological safety": -3, "Team trust": -2},
                    {"Urgency": 1, "Ambiguity": 2, "Emotional load": 2},
                    f"The {stakeholder} acknowledges the process, but the thread quietens without confirming whether the pathway solved the problem.",
                    {
                        "trigger_scene": 6,
                        "text": "The earlier boundary may have been appropriate, but the requester still seems unclear about why the pathway matters.",
                        "effects": {"Team trust": -3, "Psychological safety": -3, "Role clarity": -2},
                        "system_effects": {"Ambiguity": 4, "Emotional load": 3},
                        "reaction": "The relationship is intact, but the rationale needs repair if the process is to feel helpful rather than distant.",
                        "tags": ["respectful boundary-setting", "explaining rationale"],
                    },
                    True,
                ),
            ],
        },
        {
            "time": "10:00 am",
            "title": "Ambiguous request",
            "narrative": request,
            "situation": f"The ask matters, but ownership, scope and decision rights are not yet clear. In this {role.lower()} posture, your response may be read as advice, agreement or permission.",
            "options": [
                option(
                    "Map the decision",
                    "Name what is known, what is unknown, who needs to decide, and what advice you are actually being asked to provide.",
                    "Separates advice, decision-making and implementation before they blur together.",
                    "Can feel like process work when people are hoping for a simple answer.",
                    "The group still has to decide whether the timeline is realistic.",
                    ["clarifying ownership", "checking assumptions", "explaining rationale"],
                    {"Role clarity": 10, "Psychological safety": 3, "Team trust": 3, "Workload pressure": -2},
                    {"Ambiguity": -10, "Urgency": 2},
                    "A colleague says the framing helps, while another person looks concerned that the next step may take longer than expected.",
                    {
                        "trigger_scene": 7,
                        "text": "Because the decision roles were named earlier, the end-of-day wrap has fewer surprises. The pressure is still real, but the work is easier to sequence.",
                        "effects": {"Role clarity": 4, "Team trust": 3, "Workload pressure": -2},
                        "system_effects": {"Ambiguity": -4},
                        "reaction": "People can see the open questions without treating them as personal failures.",
                        "tags": ["clarifying ownership"],
                    },
                ),
                option(
                    "Offer a provisional expert view",
                    "Give your best advice with a clear caveat about the context you have not yet tested.",
                    "Helps the work progress and translates complexity into something usable.",
                    "Your expertise may carry more weight than intended and close down local judgement.",
                    "The local constraints and stakeholder perspectives still need to be checked.",
                    ["translating complexity", "checking assumptions"],
                    {"Workload pressure": -3, "Team trust": 3, "Role clarity": -3, "Psychological safety": -1},
                    {"Urgency": -3, "Ambiguity": 3, "Visibility to senior stakeholders": 2},
                    "The group appreciates having a direction, though the caveat is easy to lose once the advice is repeated.",
                    {
                        "trigger_scene": 6,
                        "text": "Your provisional advice is now being quoted as a settled answer. It helped progress, but the caveat has dropped out of the retelling.",
                        "effects": {"Role clarity": -4, "Psychological safety": -2, "Workload pressure": 3},
                        "system_effects": {"Ambiguity": 5, "Visibility to senior stakeholders": 4},
                        "reaction": "The work has momentum, but the system is converting advice into permission faster than the context can catch up.",
                        "tags": ["translating complexity"],
                    },
                    True,
                ),
                option(
                    "Open up the context",
                    "Ask what success would look like for students, staff and the relevant process owner before proposing options.",
                    "Makes room for purpose, local context and missing constraints.",
                    "May widen the conversation when the group is already feeling time pressure.",
                    "Someone still needs to turn the broader context into a decision and next action.",
                    ["connecting to shared purpose", "inviting missing voices", "checking assumptions"],
                    {"Inclusion climate": 7, "Psychological safety": 5, "Role clarity": 3, "Workload pressure": 2},
                    {"Ambiguity": -4, "Urgency": 3, "Cross-team dependency": 2},
                    "Someone adds a constraint that had not been visible, but the group now needs a tighter frame to avoid expanding the work indefinitely.",
                ),
            ],
        },
        {
            "time": "11:15 am",
            "title": "Team interaction",
            "narrative": f"In a team huddle, a quieter colleague mentions a concern about {profile['pressures'][1] if len(profile['pressures']) > 1 else pressure}. The meeting is moving quickly because another group is waiting for a response.",
            "situation": "The group is close to agreement. The concern may be a genuine risk, or it may need to be parked carefully so the work can continue.",
            "open_text": "Write one sentence you could use to invite a quieter colleague into the conversation without putting them on the spot.",
            "noticing_pause": "What became more visible because of your choice, and what might still be hidden?",
            "options": [
                option(
                    "Invite the concern carefully",
                    "Pause and ask whether the concern changes the next step or needs a focused follow-up with the right people.",
                    "Creates room for a risk before the decision hardens.",
                    "Can slow momentum and may put attention on the colleague if handled clumsily.",
                    "The group still needs to decide who owns the follow-up.",
                    ["inviting missing voices", "preserving dignity", "checking assumptions"],
                    {"Inclusion climate": 9, "Psychological safety": 6, "Team trust": 3, "Workload pressure": 2},
                    {"Ambiguity": -3, "Urgency": 2, "Emotional load": -1},
                    "The colleague contributes one useful risk, and the conversation becomes more grounded. The owner for the follow-up still needs to be named.",
                ),
                option(
                    "Park it with an owner",
                    "Acknowledge the concern, put it in the notes, and name who will decide whether it changes the plan.",
                    "Keeps the concern visible without letting the meeting expand indefinitely.",
                    "The colleague may not feel fully heard if the follow-up is too procedural.",
                    "The quality of the later follow-up will determine whether the concern actually shapes the work.",
                    ["making workload visible", "clarifying ownership", "respectful boundary-setting"],
                    {"Workload pressure": -2, "Role clarity": 5, "Inclusion climate": 1},
                    {"Urgency": -2, "Ambiguity": -2, "Emotional load": 1},
                    "The meeting keeps moving, though the room depends on the named owner to make the parked concern real rather than symbolic.",
                ),
                option(
                    "Stay with the emerging agreement",
                    "Let the decision proceed because the group has limited time and most people seem ready to move.",
                    "Protects momentum and reduces immediate meeting load.",
                    "A quieter risk may remain outside the formal decision.",
                    "If the concern matters, it may return later as rework or a side-channel message.",
                    ["calm under pressure", "naming trade-offs"],
                    {"Workload pressure": -4, "Inclusion climate": -7, "Psychological safety": -4, "Team trust": -2},
                    {"Urgency": -3, "Ambiguity": 4, "Emotional load": 2},
                    "The group moves on efficiently, but the colleague does not contribute again in the meeting.",
                    {
                        "trigger_scene": 6,
                        "text": "The quieter colleague sends a side message raising the risk that was not discussed. The work is moving, but one important concern stayed outside the room.",
                        "effects": {"Inclusion climate": -6, "Psychological safety": -4, "Role clarity": -2},
                        "system_effects": {"Ambiguity": 4, "Emotional load": 4},
                        "reaction": "The message is constructive, but it shows that the meeting process did not fully hold the risk.",
                        "tags": ["inviting missing voices"],
                    },
                    True,
                ),
            ],
        },
        {
            "time": "1:00 pm",
            "title": "Cross-team dependency",
            "narrative": f"After lunch, the work touches another ITaLI team and {third_stakeholder}. A dependency is real, but everyone is using slightly different language.",
            "situation": "System pressure is shaping the moment: urgency and ambiguity make a quick workaround attractive, while cross-team dependency makes assumptions costly.",
            "options": [
                option(
                    "Translate the dependency",
                    "Summarise the shared purpose, name the dependency, and suggest a short owner-to-owner check-in.",
                    "Turns vague cross-team reliance into a visible coordination task.",
                    "Adds another conversation to a day that already feels full.",
                    "The other team still has its own capacity and timing constraints.",
                    ["translating complexity", "connecting to shared purpose", "clarifying ownership"],
                    {"Role clarity": 8, "Team trust": 5, "Workload pressure": 1},
                    {"Cross-team dependency": -6, "Ambiguity": -4, "Urgency": 1},
                    "The other team appreciates the clearer framing and names a timing constraint that still needs a priority call.",
                ),
                option(
                    "Escalate the priority",
                    "Ask a senior colleague to make the call because the timeline and visibility are increasing.",
                    "Creates decision visibility and may unblock conflicting priorities.",
                    "Can reduce local agency if the escalation bypasses people closest to the work.",
                    "The senior decision still needs enough context to avoid a blunt trade-off.",
                    ["escalating appropriately", "naming trade-offs", "explaining rationale"],
                    {"Role clarity": 5, "Workload pressure": -3, "Inclusion climate": -2, "Team trust": 1},
                    {"Visibility to senior stakeholders": 8, "Urgency": -2, "Emotional load": 2},
                    "The priority becomes visible, though one colleague worries that escalation may flatten important local detail.",
                ),
                option(
                    "Work around it for now",
                    "Continue with your part and assume the dependency can be sorted out when the other team is ready.",
                    "Maintains local momentum and avoids pulling more people into the issue immediately.",
                    "Creates handover risk and may surprise the people who own the dependency.",
                    "The dependency is unresolved and may return as rework.",
                    ["calm under pressure"],
                    {"Workload pressure": 4, "Role clarity": -7, "Team trust": -3},
                    {"Cross-team dependency": 7, "Ambiguity": 5, "Urgency": -1},
                    "The work moves, but the dependency remains in the background and is now less visible to the people who need to shape it.",
                    {
                        "trigger_scene": 7,
                        "text": "The workaround reaches the end of the day with a handover gap. No one acted in bad faith, but the dependency was left too implicit.",
                        "effects": {"Role clarity": -5, "Team trust": -4, "Workload pressure": 5},
                        "system_effects": {"Cross-team dependency": 6, "Ambiguity": 5},
                        "reaction": "The issue can still be repaired, but it now requires a clearer handover and a less defensive tone.",
                        "tags": ["clarifying ownership", "repairing misunderstanding"],
                    },
                    True,
                ),
            ],
        },
        {
            "time": "2:30 pm",
            "title": "Workload pressure moment",
            "narrative": f"A second request arrives while the morning work is still active. For {team}, this is the kind of moment where '{behaviour}' has to be balanced with sustainable work.",
            "situation": "No one is trying to overload the system, but the combined effect is starting to exceed the available time.",
            "noticing_pause": "Who might still be carrying hidden work after this moment?",
            "options": [
                option(
                    "Name the trade-off",
                    "Explain what can be done today, what would need to move, and what decision is needed about priority.",
                    "Turns pressure into a shared prioritisation question rather than a private endurance test.",
                    "Can disappoint people who were hoping the extra request would simply be absorbed.",
                    "The organisation still needs a real stop, pause or sequence decision.",
                    ["naming trade-offs", "making workload visible", "respectful boundary-setting"],
                    {"Workload pressure": -8, "Role clarity": 6, "Psychological safety": 4, "Team trust": 2},
                    {"Urgency": 2, "Ambiguity": -5, "Emotional load": -3, "Visibility to senior stakeholders": 2},
                    "A colleague says it helps to see the actual choices, though the requester still looks worried about the deadline.",
                ),
                option(
                    "Ask for defined help",
                    "Identify a specific task another person could pick up and ask for short-term support.",
                    "Shares load and creates a clearer path through the afternoon.",
                    "Coordination takes time and may move pressure to someone whose capacity is also constrained.",
                    "The underlying volume of work has not changed.",
                    ["making workload visible", "connecting to shared purpose", "recognising hidden work"],
                    {"Workload pressure": -5, "Team trust": 4, "Role clarity": 2, "Inclusion climate": 2},
                    {"Cross-team dependency": 2, "Emotional load": -2},
                    "Someone offers to take one defined piece, while another person notes that this only works if the scope stays contained.",
                ),
                option(
                    "Keep absorbing",
                    "Decide it is easier to do it yourself than renegotiate expectations in the middle of the day.",
                    "Protects others from immediate friction and may get the visible work done.",
                    "The real workload cost stays hidden and becomes harder to discuss later.",
                    "The system learns less about the capacity problem.",
                    ["calm under pressure"],
                    {"Workload pressure": 10, "Psychological safety": -4, "Role clarity": -5, "Team trust": 1},
                    {"Urgency": 4, "Emotional load": 6, "Ambiguity": 3},
                    "Others experience you as helpful, but the response reduces the evidence that priorities need to be renegotiated.",
                    {
                        "trigger_scene": 6,
                        "text": "The absorbed work has become today's hidden labour. The output may still happen, but the workload signal is weak.",
                        "effects": {"Workload pressure": 8, "Psychological safety": -3, "Role clarity": -3},
                        "system_effects": {"Emotional load": 5, "Urgency": 3},
                        "reaction": "The team appreciates the help, but no one has enough information to make a sustainable priority decision.",
                        "tags": ["making workload visible"],
                    },
                    True,
                ),
            ],
        },
        {
            "time": "3:20 pm",
            "title": "Midday repair and message moment",
            "narrative": "A message thread is becoming compressed and slightly tense. People are making different assumptions about scope, urgency and ownership.",
            "situation": "You have a chance to write a short response that clarifies the work and repairs any confusion before it becomes personal.",
            "open_text": "Write the message you would send to clarify ownership, scope or next steps while preserving the relationship.",
            "repair_scene": True,
            "options": [
                option(
                    "Repair with clarity and warmth",
                    "Name that the thread may be carrying different assumptions, then clarify ownership, timing and the next check-in.",
                    "Reduces ambiguity and lowers relational tension without pretending the pressure has disappeared.",
                    "Can read as slowing the thread if people wanted a quick yes or no.",
                    "The priority decision still has to be made by the right owner.",
                    ["repairing misunderstanding", "clarifying ownership", "preserving dignity"],
                    {"Role clarity": 8, "Psychological safety": 6, "Team trust": 5, "Workload pressure": -1},
                    {"Ambiguity": -7, "Emotional load": -5},
                    "The thread becomes easier to continue, although the requester still needs a decision about what can move.",
                    {
                        "trigger_scene": 7,
                        "text": "Your repair message has reduced tension. The issue is not fully solved, but the conversation is easier to continue.",
                        "effects": {"Team trust": 7, "Psychological safety": 6},
                        "system_effects": {"Emotional load": -5, "Ambiguity": -2},
                        "reaction": "People return to the work with less defensiveness and a clearer next step.",
                        "tags": ["repairing misunderstanding"],
                    },
                ),
                option(
                    "Explain the pathway",
                    "Reply with the relevant process, explain why it protects fairness or quality, and offer one practical next step.",
                    "Makes the process more intelligible and less like a wall.",
                    "May still feel bureaucratic if the immediate pressure is not acknowledged.",
                    "The person may need help translating the pathway into their specific situation.",
                    ["explaining rationale", "respectful boundary-setting", "preserving dignity"],
                    {"Role clarity": 5, "Inclusion climate": 1, "Team trust": 1},
                    {"Ambiguity": -4, "Emotional load": 1},
                    "The response gives people a route forward, though one stakeholder still appears concerned about time.",
                ),
                option(
                    "Wait for a better answer",
                    "Leave the thread until you have enough time to respond properly.",
                    "Avoids a rushed or defensive message.",
                    "Silence increases uncertainty when people are already reading urgency into the thread.",
                    "Others still do not know who owns the next step.",
                    ["checking assumptions"],
                    {"Workload pressure": 2, "Role clarity": -4, "Psychological safety": -2},
                    {"Ambiguity": 4, "Emotional load": 3},
                    "Someone else asks for an update. The delay is understandable, but the thread now carries more uncertainty.",
                    {
                        "trigger_scene": 7,
                        "text": "The delayed reply left people uncertain for longer than intended. It can still be repaired with a concise next-step message.",
                        "effects": {"Role clarity": -3, "Team trust": -2},
                        "system_effects": {"Ambiguity": 4, "Emotional load": 2},
                        "reaction": "The issue is not dramatic, but it now needs a clearer closing signal.",
                        "tags": ["repairing misunderstanding", "clarifying ownership"],
                    },
                    True,
                ),
            ],
        },
        {
            "time": "4:10 pm",
            "title": "Repair opportunity",
            "narrative": "You notice that one part of the day may have landed less well than intended. Repair here is not about blame. It is about making the next conversation easier and the work clearer.",
            "situation": "Earlier choices may have helped with speed, boundaries or expert advice, while also creating hidden workload, uncertainty or a missed voice.",
            "open_text": "Write a repair message after realising your earlier response may have closed down discussion.",
            "repair_scene": True,
            "noticing_pause": "What would be worth clarifying before the day continues?",
            "options": [
                option(
                    "Repair specifically",
                    "Name the impact, clarify your intent, and invite the missing information or voice back in.",
                    "Restores dignity and gives people a safe path back into the conversation.",
                    "Requires care so the repair does not become a long apology that shifts attention away from the work.",
                    "The task still needs ownership, scope and priority to be clarified.",
                    ["repairing misunderstanding", "inviting missing voices", "preserving dignity"],
                    {"Psychological safety": 10, "Inclusion climate": 7, "Team trust": 8, "Role clarity": 2},
                    {"Emotional load": -7, "Ambiguity": -2},
                    "The colleague re-engages and adds helpful context. The atmosphere improves, though the work still needs a named next step.",
                ),
                option(
                    "Repair through next steps",
                    "Send a follow-up that explains the rationale, names the trade-off and sets out who will do what next.",
                    "Turns tension into practical clarity without over-personalising the issue.",
                    "May miss the relational impact if the person mainly needed acknowledgement.",
                    "The relationship may still benefit from a more direct check-in later.",
                    ["repairing misunderstanding", "explaining rationale", "clarifying ownership", "naming trade-offs"],
                    {"Role clarity": 8, "Team trust": 5, "Psychological safety": 4},
                    {"Ambiguity": -6, "Emotional load": -2},
                    "The thread becomes more constructive, though one person may still need a quieter follow-up to feel fully heard.",
                ),
                option(
                    "Let it settle for now",
                    "Assume the moment will pass and focus on finishing the visible work.",
                    "Avoids adding another message to a crowded afternoon.",
                    "Leaves uncertainty in the relationship and may make the next interaction more cautious.",
                    "The work may close today with an avoidable relational or role-clarity edge.",
                    ["calm under pressure"],
                    {"Workload pressure": -2, "Psychological safety": -5, "Inclusion climate": -4, "Team trust": -4},
                    {"Emotional load": 4, "Ambiguity": 2},
                    "The day continues, but the unresolved tone remains lightly present in later messages.",
                    None,
                    True,
                ),
            ],
        },
        {
            "time": "4:55 pm",
            "title": "End-of-day wrap",
            "narrative": f"The formal day is nearly done. In {team}, the work will continue through systems, relationships and tomorrow's priorities.",
            "situation": "This is a second repair opportunity: a chance to close role clarity, relational tone or sustainable-work signals before people carry ambiguity into tomorrow.",
            "repair_scene": True,
            "options": [
                option(
                    "Close the loop",
                    "Send a brief wrap-up with decisions, owners, open questions and one appreciation for hidden work.",
                    "Gives people clearer next steps and recognises effort without pretending everything is solved.",
                    "Can create an expectation that you will always provide the coordination layer.",
                    "Tomorrow still needs a priority check if new requests arrive.",
                    ["clarifying ownership", "recognising hidden work", "connecting to shared purpose"],
                    {"Role clarity": 8, "Team trust": 7, "Inclusion climate": 3, "Workload pressure": -3},
                    {"Ambiguity": -6, "Emotional load": -3},
                    "A colleague says the summary helps for tomorrow, while another adds one open question that still needs a decision owner.",
                ),
                option(
                    "Protect tomorrow's capacity",
                    "Name what is complete, what is not, and what needs a priority decision before more work is accepted.",
                    "Avoids turning unfinished work into private catch-up and makes sustainable work discussable.",
                    "May feel uncomfortable if others expected a more polished close.",
                    "A leader or owner still needs to make a sequencing decision.",
                    ["making workload visible", "naming trade-offs", "respectful boundary-setting"],
                    {"Workload pressure": -8, "Role clarity": 5, "Psychological safety": 4, "Team trust": 1},
                    {"Urgency": 2, "Ambiguity": -5, "Emotional load": -2, "Visibility to senior stakeholders": 3},
                    "The unfinished work is visible without blame, though it now requires someone with decision rights to act on the trade-off.",
                ),
                option(
                    "Finish quietly",
                    "Keep working quietly and leave the wrap-up until the morning.",
                    "Preserves a little time now and avoids sending an imperfect late-day message.",
                    "Others may start tomorrow with avoidable uncertainty about decisions and ownership.",
                    "The work remains mostly in your head overnight.",
                    ["calm under pressure"],
                    {"Workload pressure": 3, "Role clarity": -5, "Team trust": -3},
                    {"Ambiguity": 4, "Emotional load": 2},
                    "The visible day ends calmly, but tomorrow's first conversation will need to reconstruct what changed and what remains open.",
                    None,
                    True,
                ),
            ],
        },
    ]


def init_state():
    defaults = {
        "stage": "welcome",
        "team": None,
        "role": None,
        "scene_index": 0,
        "climate": deepcopy(CLIMATE_START),
        "system_pressures": deepcopy(SYSTEM_PRESSURE_START),
        "decisions": [],
        "open_text_responses": [],
        "noticing_responses": [],
        "behaviour_tags": [],
        "repair_flags": [],
        "feedback_history": [],
        "delayed_consequences": [],
        "applied_delayed_consequences": [],
        "final_profile": None,
        "last_feedback": None,
        "pending_option": None,
        "setup_team": TEAMS[0],
        "setup_role": ROLE_POSTURES[0],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_simulation():
    for key in [
        "stage",
        "team",
        "role",
        "scene_index",
        "climate",
        "system_pressures",
        "decisions",
        "open_text_responses",
        "noticing_responses",
        "behaviour_tags",
        "repair_flags",
        "feedback_history",
        "delayed_consequences",
        "applied_delayed_consequences",
        "final_profile",
        "last_feedback",
        "pending_option",
    ]:
        st.session_state.pop(key, None)
    init_state()


def commit_setup_selection():
    st.session_state.team = st.session_state.setup_team
    st.session_state.role = st.session_state.setup_role
    st.session_state.scene_index = 0
    st.session_state.climate = deepcopy(CLIMATE_START)
    st.session_state.system_pressures = deepcopy(SYSTEM_PRESSURE_START)
    st.session_state.decisions = []
    st.session_state.open_text_responses = []
    st.session_state.noticing_responses = []
    st.session_state.behaviour_tags = []
    st.session_state.repair_flags = []
    st.session_state.feedback_history = []
    st.session_state.delayed_consequences = []
    st.session_state.applied_delayed_consequences = []
    st.session_state.final_profile = None
    st.session_state.last_feedback = None
    st.session_state.stage = "day_setup"


def clamp(value: int) -> int:
    return max(0, min(100, value))


def apply_effects(effects: dict[str, int]):
    for indicator, change in effects.items():
        st.session_state.climate[indicator] = clamp(st.session_state.climate[indicator] + change)


def apply_system_effects(effects: dict[str, int]):
    for pressure, change in effects.items():
        st.session_state.system_pressures[pressure] = clamp(st.session_state.system_pressures[pressure] + change)


def format_effects(effects: dict[str, int]) -> str:
    parts = []
    for key, value in effects.items():
        sign = "+" if value > 0 else ""
        parts.append(f"{key} {sign}{value}")
    return ", ".join(parts)


def validate_scenario_maturity(scenes: list[dict]) -> list[str]:
    required = {"helps", "risk", "unresolved", "effects", "tags", "reaction"}
    warnings = []
    for scene in scenes:
        for opt in scene.get("options", []):
            missing = [field for field in required if not opt.get(field)]
            if missing:
                warnings.append(f"{scene['title']} / {opt.get('label', 'Unnamed option')} missing: {', '.join(missing)}")
    return warnings


def due_delayed_consequences(scene_index: int) -> list[dict]:
    due = []
    for idx, item in enumerate(st.session_state.delayed_consequences):
        if item["trigger_scene"] == scene_index and idx not in st.session_state.applied_delayed_consequences:
            apply_effects(item.get("effects", {}))
            apply_system_effects(item.get("system_effects", {}))
            st.session_state.applied_delayed_consequences.append(idx)
            st.session_state.feedback_history.append({"delayed": True, **item})
            due.append(item)
    return due


def system_pressure_context() -> str:
    pressures = st.session_state.system_pressures
    highest = sorted(pressures.items(), key=lambda item: item[1], reverse=True)[:2]
    return f"{highest[0][0].lower()} is high and {highest[1][0].lower()} is also shaping the moment"


@st.cache_data(show_spinner=False)
def image_data_url(path: str) -> str:
    image_path = Path(path)
    if not image_path.exists():
        return ""
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def indicator_help(name: str) -> str:
    if name == "Workload pressure":
        return "Higher means more pressure."
    return "Higher means the climate is stronger."


SCENE_TRANSITIONS = [
    "The day opens with individual triage and early signals about hidden work.",
    "The workday shifts from a small ask to ambiguity about advice, ownership and decision rights.",
    "Attention moves into the team room, where pace and participation start to interact.",
    "The work expands beyond one team, making dependency and handover risk more visible.",
    "Pressure concentrates around capacity, priority and what can realistically move today.",
    "The day moves into written communication, where tone, timing and clarity carry extra weight.",
    "A repair window opens: notice impact, restore clarity and reopen the conversation.",
    "The workday closes with choices about what gets carried into tomorrow.",
]

STATUS_LABELS = [
    "Morning setup",
    "Ambiguity rising",
    "Team interaction",
    "Cross-team dependency",
    "Pressure point",
    "Message practice",
    "Repair window",
    "End-of-day reflection",
]


def inject_custom_css():
    hero_url = image_data_url(str(HERO_IMAGE))
    if hero_url:
        st.markdown(f"<style>:root {{--hero-image: url('{hero_url}');}}</style>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        :root {
            --ink: #172126;
            --muted: #5d6870;
            --soft: #f5f2ed;
            --card: #fffdf9;
            --line: #ded7cd;
            --line-strong: #c9beb1;
            --plum: #5b3f73;
            --plum-soft: #efe9f3;
            --amber: #9b681e;
            --amber-soft: #fff4df;
            --teal: #2e7468;
            --teal-soft: #e8f3f0;
            --navy: #243947;
            --shadow: 0 18px 45px rgba(23, 33, 38, .10);
            --shadow-soft: 0 10px 24px rgba(23, 33, 38, .07);
        }
        .stApp {
            background:
                radial-gradient(circle at 12% 10%, rgba(91, 63, 115, .16), transparent 28rem),
                radial-gradient(circle at 92% 2%, rgba(46, 116, 104, .12), transparent 30rem),
                linear-gradient(180deg, #faf8f4 0%, var(--soft) 58%, #f1eee8 100%);
            color: var(--ink);
        }
        .block-container { padding-top: 1.1rem; padding-bottom: 3rem; max-width: 1480px; }
        h1, h2, h3 { letter-spacing: 0; }
        .app-shell { display: block; }
        .hero-card, .sim-header, .role-card, .scene-stage, .hud-card, .feedback-card,
        .repair-card, .delayed-card, .profile-card, .replay-card, .output-panel,
        .message-card, .calendar-card, .decision-card {
            background: rgba(255, 253, 249, .96);
            border: 1px solid var(--line);
            border-radius: 12px;
            box-shadow: var(--shadow-soft);
        }
        .hero-card {
            position: relative;
            overflow: hidden;
            padding: 2rem;
            box-shadow: var(--shadow);
            border-top: 5px solid var(--plum);
            min-height: 360px;
            display: flex;
            align-items: flex-end;
            isolation: isolate;
        }
        .hero-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background-image: var(--hero-image);
            background-size: cover;
            background-position: center right;
            opacity: .58;
            z-index: -2;
        }
        .hero-card::after {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, rgba(255,253,249,.98) 0%, rgba(255,253,249,.87) 42%, rgba(255,253,249,.48) 70%, rgba(255,253,249,.22) 100%),
                linear-gradient(180deg, rgba(23,33,38,.04), rgba(23,33,38,.18));
            z-index: -1;
        }
        .hero-content {
            max-width: 800px;
        }
        .hero-card h1 { font-size: 3rem; margin: .1rem 0 .35rem 0; }
        .hero-lede { font-size: 1.2rem; max-width: 900px; color: var(--navy); line-height: 1.55; }
        .sim-header {
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
            border-top: 4px solid var(--plum);
            background:
                linear-gradient(90deg, rgba(255,253,249,.96), rgba(239,233,243,.88)),
                radial-gradient(circle at 100% 0%, rgba(46,116,104,.18), transparent 18rem);
        }
        .sim-header-grid {
            display: grid;
            grid-template-columns: minmax(240px, 1.4fr) repeat(3, minmax(120px, .55fr));
            gap: .8rem;
            align-items: center;
        }
        .sim-title { font-size: 1.45rem; font-weight: 760; color: var(--ink); margin: 0; }
        .sim-subtitle { color: var(--muted); margin-top: .15rem; }
        .sim-stat-label { color: var(--muted); font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; }
        .sim-stat-value { font-weight: 720; color: var(--navy); margin-top: .15rem; }
        .phase-pill {
            display: inline-block;
            border: 1px solid var(--line-strong);
            background: var(--plum-soft);
            color: #3b264e;
            border-radius: 999px;
            padding: .22rem .62rem;
            font-size: .74rem;
            font-weight: 720;
            text-transform: uppercase;
            letter-spacing: .06em;
            margin-bottom: .55rem;
        }
        .role-card, .hud-card { padding: 1rem; margin-bottom: .85rem; }
        .role-card h3, .hud-card h3 { margin: .15rem 0 .45rem; font-size: 1.05rem; }
        .small-label {
            color: var(--muted);
            font-size: .72rem;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-weight: 760;
        }
        .muted { color: var(--muted); }
        .scene-stage {
            padding: 1.25rem;
            border-top: 5px solid var(--navy);
            box-shadow: var(--shadow);
            background:
                linear-gradient(135deg, rgba(255,253,249,.98), rgba(255,253,249,.92)),
                radial-gradient(circle at 94% 8%, rgba(91,63,115,.16), transparent 18rem);
        }
        .scene-stage h2 { margin-top: .15rem; font-size: 1.75rem; }
        .transition-card {
            border: 1px solid var(--line);
            background: #fbf7f1;
            border-radius: 10px;
            padding: .85rem 1rem;
            margin-bottom: .9rem;
            color: var(--navy);
        }
        .message-card, .calendar-card {
            padding: 1rem;
            margin: 1rem 0;
            border-left: 5px solid var(--plum);
            position: relative;
        }
        .message-card::before, .calendar-card::before {
            content: "";
            position: absolute;
            top: .8rem;
            right: .9rem;
            width: 3.2rem;
            height: 3.2rem;
            border-radius: 999px;
            border: 1px solid rgba(91,63,115,.16);
            background: radial-gradient(circle, rgba(91,63,115,.14), transparent 62%);
        }
        .message-meta { color: var(--muted); font-size: .82rem; margin-bottom: .35rem; }
        .message-body { font-size: 1.02rem; line-height: 1.55; color: var(--ink); }
        .decision-card {
            padding: 1rem;
            margin: .85rem 0 1rem;
            border-left: 5px solid var(--line-strong);
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
        }
        .decision-card:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow);
            border-left-color: var(--plum);
        }
        .decision-title { font-size: 1.08rem; font-weight: 760; color: var(--ink); margin-bottom: .4rem; }
        .decision-meta { color: var(--muted); line-height: 1.45; margin-bottom: .55rem; }
        .decision-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .65rem;
            margin-top: .75rem;
        }
        .trade-box {
            background: #fbf8f2;
            border: 1px solid var(--line);
            border-radius: 9px;
            padding: .65rem;
            line-height: 1.35;
        }
        .tag-chip, .bd-pill {
            display: inline-block;
            padding: .18rem .55rem;
            border-radius: 999px;
            border: 1px solid #cfd9d6;
            background: var(--teal-soft);
            color: #244f48;
            font-size: .78rem;
            margin: .12rem .18rem .12rem 0;
            font-weight: 650;
        }
        .feedback-card {
            padding: 1rem;
            margin-top: 1rem;
            border-left: 5px solid var(--teal);
            background:
                linear-gradient(135deg, rgba(255,253,249,.98), rgba(232,243,240,.78));
        }
        .feedback-card h3 { margin-top: 0; }
        .change-chip {
            display: inline-block;
            border-radius: 999px;
            padding: .22rem .58rem;
            margin: .12rem .18rem .12rem 0;
            border: 1px solid var(--line-strong);
            background: #f7f4ee;
            color: var(--navy);
            font-weight: 720;
            font-size: .82rem;
        }
        .repair-card {
            padding: 1rem;
            margin: 1rem 0;
            border-left: 5px solid var(--teal);
            background: linear-gradient(135deg, #fffdf9 0%, var(--teal-soft) 100%);
        }
        .delayed-card {
            padding: 1rem;
            margin: .9rem 0;
            border-left: 5px solid var(--amber);
            background: var(--amber-soft);
        }
        .practice-card {
            border: 1px solid var(--line);
            background: #fbf8f2;
            border-radius: 10px;
            padding: .9rem 1rem;
            margin: 1rem 0 .45rem;
        }
        .hud-row { margin-bottom: .75rem; }
        .hud-tile {
            border: 1px solid var(--line);
            border-radius: 11px;
            padding: .72rem;
            background: linear-gradient(180deg, #fffdf9, #fbf8f2);
            margin-bottom: .55rem;
        }
        .hud-top {
            display: flex;
            justify-content: space-between;
            gap: .6rem;
            align-items: baseline;
        }
        .hud-name { font-weight: 760; color: var(--ink); }
        .hud-value { font-weight: 760; color: var(--navy); }
        .hud-bar, .pressure-meter {
            height: 8px;
            background: #ece5dc;
            border-radius: 999px;
            overflow: hidden;
            margin: .32rem 0 .18rem;
        }
        .hud-fill { height: 100%; background: var(--plum); border-radius: 999px; }
        .pressure-fill { height: 100%; background: var(--amber); border-radius: 999px; }
        .pressure-chip {
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: .55rem .65rem;
            margin-bottom: .5rem;
            background: #fbf8f2;
        }
        .timeline { display: flex; flex-direction: column; gap: .42rem; margin-top: .65rem; }
        .timeline-item {
            border: 1px solid var(--line);
            background: #fbf8f2;
            border-radius: 9px;
            padding: .55rem .62rem;
            position: relative;
        }
        .timeline-item::before {
            content: "";
            display: inline-block;
            width: .48rem;
            height: .48rem;
            border-radius: 999px;
            margin-right: .4rem;
            background: var(--line-strong);
        }
        .timeline-current {
            border-color: var(--plum);
            background: var(--plum-soft);
            box-shadow: inset 4px 0 0 var(--plum);
        }
        .timeline-complete {
            border-color: #bed6cf;
            background: var(--teal-soft);
        }
        .timeline-upcoming { opacity: .78; }
        .timeline-title { font-weight: 720; font-size: .86rem; }
        .timeline-meta { color: var(--muted); font-size: .78rem; }
        .profile-card {
            padding: 1.35rem;
            border-top: 5px solid var(--plum);
            box-shadow: var(--shadow);
            background:
                linear-gradient(135deg, rgba(255,253,249,.98), rgba(239,233,243,.72)),
                radial-gradient(circle at 90% 15%, rgba(46,116,104,.16), transparent 22rem);
        }
        .cockpit-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .7rem;
            margin-top: 1rem;
        }
        .cockpit-mini {
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: .7rem;
            background: rgba(255,253,249,.88);
        }
        .insight-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .8rem;
            margin: 1rem 0;
        }
        .insight-card {
            border: 1px solid var(--line);
            border-radius: 10px;
            background: #fffdf9;
            padding: .9rem;
        }
        .replay-card {
            padding: .9rem;
            margin: .75rem 0;
            border-left: 5px solid var(--line-strong);
        }
        .output-panel { padding: .6rem; }
        div.stButton > button {
            border-radius: 9px;
            font-weight: 720;
            border: 1px solid var(--plum);
        }
        div[data-testid="stTextArea"] textarea {
            border-radius: 10px;
            border-color: var(--line-strong);
        }
        div[data-testid="stMetric"] {
            background: rgba(255,253,249,.92);
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: .7rem .8rem;
        }
        @media (max-width: 900px) {
            .sim-header-grid, .decision-grid, .insight-grid { grid-template-columns: 1fr; }
            .hero-card h1 { font-size: 2.2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


render_css = inject_custom_css


def tag_chips(tags: list[str]) -> str:
    return "".join(f'<span class="tag-chip">{escape(tag)}</span>' for tag in tags)


def value_level(value: int) -> str:
    if value >= 72:
        return "High"
    if value >= 48:
        return "Medium"
    if value >= 26:
        return "Moderate"
    return "Low"


def climate_interpretation(name: str, value: int) -> str:
    if name == "Workload pressure":
        if value >= 70:
            return "rising pressure"
        if value >= 50:
            return "active pressure"
        return "easing pressure"
    if value >= 70:
        return "strengthening"
    if value >= 50:
        return "steady"
    return "needs attention"


def movement_label(change: int, workload=False) -> str:
    if change == 0:
        return "steady"
    if workload:
        return "rising" if change > 0 else "easing"
    return "improving" if change > 0 else "softening"


def render_app_header():
    if st.session_state.stage in {"simulate", "end"} and st.session_state.team:
        idx = min(st.session_state.scene_index, 7)
        status = "Debrief" if st.session_state.stage == "end" else STATUS_LABELS[idx]
        scene_label = "Complete" if st.session_state.stage == "end" else f"Scene {idx + 1} of 8"
        time_label = "End of day" if st.session_state.stage == "end" else build_scenes(st.session_state.team, st.session_state.role)[idx]["time"]
        title_label = "End-of-day debrief" if st.session_state.stage == "end" else build_scenes(st.session_state.team, st.session_state.role)[idx]["title"]
        st.markdown(
            f"""
            <div class="sim-header">
              <div class="sim-header-grid">
                <div>
                  <div class="phase-pill">Simulation cockpit</div>
                  <p class="sim-title">Better Day</p>
                  <div class="sim-subtitle">{escape(st.session_state.team)} · {escape(st.session_state.role)}</div>
                </div>
                <div><div class="sim-stat-label">Time</div><div class="sim-stat-value">{escape(time_label)}</div></div>
                <div><div class="sim-stat-label">Progress</div><div class="sim-stat-value">{escape(scene_label)}</div></div>
                <div><div class="sim-stat-label">Status</div><div class="sim-stat-value">{escape(status)} · {escape(title_label)}</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="sim-header">
              <div class="sim-header-grid">
                <div>
                  <div class="phase-pill">Prebrief</div>
                  <p class="sim-title">Better Day</p>
                  <div class="sim-subtitle">A role-personalised workday simulation for practising positive and inclusive everyday behaviours.</div>
                </div>
                <div><div class="sim-stat-label">Mode</div><div class="sim-stat-value">Reflective simulation</div></div>
                <div><div class="sim-stat-label">Focus</div><div class="sim-stat-value">Clarity · workload · inclusion</div></div>
                <div><div class="sim-stat-label">Frame</div><div class="sim-stat-value">Not an assessment</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_header():
    render_app_header()


def render_prebrief_hero():
    st.markdown(
        """
        <div class="hero-card">
          <div class="hero-content">
            <div class="phase-pill">Prebrief</div>
            <h1>Better Day</h1>
            <p class="hero-lede">Step into a simulated workday where small choices shape clarity, trust, workload and inclusion. This is reflective practice for navigating human, workload and collaboration pressures.</p>
            <div class="cockpit-strip">
              <div class="cockpit-mini"><div class="small-label">Mode</div><strong>Reflective simulation</strong></div>
              <div class="cockpit-mini"><div class="small-label">Live state</div><strong>Climate and pressure HUD</strong></div>
              <div class="cockpit-mini"><div class="small-label">Practice</div><strong>Notice · repair · reflect</strong></div>
              <div class="cockpit-mini"><div class="small-label">Frame</div><strong>Systems-aware, not a test</strong></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress():
    total = 8
    idx = st.session_state.scene_index
    if st.session_state.stage == "end":
        progress = 1.0
        label = "Workday complete"
    elif st.session_state.stage == "simulate":
        progress = idx / total
        label = f"Scene {idx + 1} of {total}"
    else:
        progress = 0.0
        label = "Orientation"
    st.caption(label)
    st.progress(progress)


def workday_timeline_html(compact=False) -> str:
    scenes = build_scenes(st.session_state.team, st.session_state.role) if st.session_state.team else []
    current = st.session_state.scene_index
    items = []
    for idx, scene in enumerate(scenes):
        if st.session_state.stage == "end" or idx < current:
            status_class = "timeline-complete"
            status = "completed"
            marker = "done"
        elif idx == current:
            status_class = "timeline-current"
            status = "current"
            marker = "now"
        else:
            status_class = "timeline-upcoming"
            status = "upcoming"
            marker = "next"
        flags = []
        if scene.get("repair_scene"):
            flags.append("repair")
        if scene.get("open_text"):
            flags.append("practice")
        flag_text = f" · {', '.join(flags)}" if flags else ""
        title = scene["title"] if not compact else scene["title"].replace(" opportunity", "")
        items.append(
            f'<div class="timeline-item {status_class}"><div class="timeline-title">{escape(scene["time"])} · {escape(title)}</div><div class="timeline-meta">{status} · {marker}{escape(flag_text)}</div></div>'
        )
    return '<div class="timeline">' + "".join(items) + "</div>"


def render_workday_timeline(compact=False):
    st.markdown(workday_timeline_html(compact), unsafe_allow_html=True)


def render_climate_hud():
    rows = []
    for name, value in st.session_state.climate.items():
        change = None
        if st.session_state.last_feedback and name in st.session_state.last_feedback["effects"]:
            change = st.session_state.last_feedback["effects"][name]
        movement = "steady" if change is None else f"{movement_label(change, name == 'Workload pressure')} · {change:+d}"
        help_text = "Higher means more pressure." if name == "Workload pressure" else "Higher means stronger climate."
        rows.append(
            f'<div class="hud-row"><div class="hud-top"><span class="hud-name">{escape(name)}</span><span class="hud-value">{value}</span></div><div class="hud-bar" aria-label="{escape(name)} {value} out of 100"><div class="hud-fill" style="width:{value}%"></div></div><div class="timeline-meta">{escape(climate_interpretation(name, value))} · {escape(movement)} · {escape(help_text)}</div></div>'
        )
    st.markdown(
        f'<div class="hud-card"><div class="small-label">Live climate HUD</div><h3>Climate indicators</h3>{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def render_climate_dashboard():
    render_climate_hud()


def render_system_pressure_panel():
    chips = []
    for name, value in st.session_state.system_pressures.items():
        chips.append(
            f'<div class="pressure-chip"><div class="hud-top"><span class="hud-name">{escape(name)}</span><span class="hud-value">{value_level(value)}</span></div><div class="pressure-meter" aria-label="{escape(name)} pressure {value} out of 100"><div class="pressure-fill" style="width:{value}%"></div></div><div class="timeline-meta">Context pressure · {value}/100</div></div>'
        )
    st.markdown(
        f'<div class="hud-card"><div class="small-label">Pressure weather</div><h3>Today\'s pressure pattern</h3><p class="muted">These are environmental conditions, not personal scores.</p>{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def render_role_panel():
    team = st.session_state.team
    role = st.session_state.role
    if not team or not role:
        return
    profile = TEAM_PROFILES[team]
    stakeholders = ", ".join(profile["stakeholders"][:4])
    focus = ", ".join(profile["positive_behaviours"][:3])
    st.markdown(
        f"""
        <div class="role-card">
          <div class="small-label">Role and state</div>
          <h3>{escape(team)}</h3>
          <p>{escape(profile["purpose"])}</p>
          <div class="small-label">Role posture</div>
          <p><strong>{escape(role)}</strong><br><span class="muted">{escape(ROLE_LENSES[role])}</span></p>
          <div class="small-label">Active stakeholders</div>
          <p>{escape(stakeholders)}</p>
          <div class="small-label">Behavioural focus</div>
          <p>{escape(focus)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="role-card">
          <div class="small-label">Workday progress</div>
          <h3>Timeline</h3>
          {workday_timeline_html(compact=True)}
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Team pressures and useful behaviours", expanded=False):
        st.markdown("**Common pressures**")
        for item in profile["pressures"]:
            st.markdown(f"- {item}")
        st.markdown("**Positive behaviours**")
        for item in profile["positive_behaviours"]:
            st.markdown(f"- {item}")


def render_message_card(sender, channel, message, timestamp):
    st.markdown(
        f"""
        <div class="message-card">
          <div class="message-meta">{escape(channel)} · {escape(timestamp)}</div>
          <div class="small-label">From: {escape(sender)}</div>
          <div class="message-body">"{escape(message)}"</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_calendar_card(title, attendees, time, pressure):
    st.markdown(
        f"""
        <div class="calendar-card">
          <div class="message-meta">Calendar alert · {escape(time)}</div>
          <div class="decision-title">{escape(title)}</div>
          <div class="decision-meta">Attendees: {escape(attendees)}</div>
          <div class="decision-meta">Pressure signal: {escape(pressure)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_delayed_consequence_card(item):
    st.markdown(
        f"""
        <div class="delayed-card">
          <div class="phase-pill">Earlier choice resurfacing</div>
          <p><strong>From {escape(item["source_scene"])}</strong></p>
          <p>{escape(item["text"])}</p>
          <p><strong>Stakeholder response:</strong> {escape(item["reaction"])}</p>
          <p class="timeline-meta">Climate: {escape(format_effects(item.get("effects", {})))} · System: {escape(format_effects(item.get("system_effects", {})))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_repair_window(text):
    st.markdown(
        f"""
        <div class="repair-card">
          <div class="phase-pill">Repair window</div>
          <h3>Notice and adjust</h3>
          <p>{escape(text)}</p>
          <p class="muted">This is a chance to restore clarity, reopen the conversation or preserve dignity without blame.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_open_text_practice_card(prompt, key, height=110):
    st.markdown(
        f"""
        <div class="practice-card">
          <div class="phase-pill">Practice moment</div>
          <h3>Write the message</h3>
          <p>{escape(prompt)}</p>
          <p class="muted">This is not scored. It will be saved for your reflection.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Show possible sentence starters", expanded=False):
        st.markdown("- I want to pause because I may have moved too quickly there.")
        st.markdown("- It would help to clarify who owns the decision and what can move if this is urgent.")
        st.markdown("- I can help with the next step, and I want to make the trade-off visible.")
    return st.text_area("Draft message", key=key, height=height, label_visibility="collapsed")


def render_noticing_pause(prompt, key):
    st.markdown(
        f"""
        <div class="practice-card">
          <div class="phase-pill">Noticing pause</div>
          <p>{escape(prompt)}</p>
          <p class="muted">Optional reflection. This is not a test.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.text_area("Noticing pause response", key=key, height=85, label_visibility="collapsed")


def render_welcome():
    render_prebrief_hero()
    st.write("")
    st.markdown(
        """
        <div class="scene-stage">
          <div class="phase-pill">Fiction contract</div>
          <p><strong>Better Day is a reflective workday simulation.</strong> It is not a test of whether you are a good colleague, and it is not a judgement of your team. You will see realistic moments where every option has some merit and some risk.</p>
          <p>The purpose is to notice how small choices shape the experience of work: what becomes clearer, what remains hidden, who is included, where pressure accumulates, and how trust can be repaired.</p>
          <p>These scenarios are fictional, but they are based on common patterns of work: ambiguity, urgency, cross-team dependency, hidden labour, competing priorities and the need to preserve respectful relationships.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="role-card"><div class="small-label">Navigate</div><h3>Realistic workday moments</h3><p>Move through ambiguity, meetings, dependency, pressure and repair.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="role-card"><div class="small-label">Watch</div><h3>Climate and pressure change</h3><p>Track live indicators and system conditions as the day unfolds.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="role-card"><div class="small-label">Practise</div><h3>Small inclusive behaviours</h3><p>Try clarifying, inviting, naming trade-offs and repairing without blame.</p></div>', unsafe_allow_html=True)
    if st.button("Begin the workday", type="primary"):
        st.session_state.stage = "setup"
        st.rerun()


def render_setup():
    st.markdown('<div class="phase-pill">Role setup</div>', unsafe_allow_html=True)
    st.subheader("Configure your simulated day")
    left, right = st.columns([1.1, 1])
    with left:
        st.selectbox(
            "ITaLI team",
            TEAMS,
            index=TEAMS.index(st.session_state.setup_team) if st.session_state.setup_team in TEAMS else 0,
            key="setup_team",
        )
        st.radio(
            "Role posture",
            ROLE_POSTURES,
            horizontal=False,
            index=ROLE_POSTURES.index(st.session_state.setup_role) if st.session_state.setup_role in ROLE_POSTURES else 0,
            key="setup_role",
        )
    with right:
        team = st.session_state.setup_team
        role = st.session_state.setup_role
        profile = TEAM_PROFILES[team]
        st.markdown(
            f"""
            <div class="scene-stage">
              <div class="phase-pill">Simulation profile</div>
              <h2>{escape(team)}</h2>
              <p>{escape(profile["purpose"])}</p>
              <div class="insight-grid">
                <div class="insight-card"><div class="small-label">Common pressures</div><p>{escape("; ".join(profile["pressures"][:4]))}</p></div>
                <div class="insight-card"><div class="small-label">Typical stakeholders</div><p>{escape(", ".join(profile["stakeholders"][:5]))}</p></div>
                <div class="insight-card"><div class="small-label">Behavioural focus</div><p>{escape(", ".join(profile["positive_behaviours"][:4]))}</p></div>
                <div class="insight-card"><div class="small-label">Role posture changes</div><p>{escape(ROLE_LENSES[role])}</p></div>
              </div>
              <div class="message-card">
                <div class="message-meta">Example work signal</div>
                <div class="message-body">"{escape(profile["requests"][0])}"</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if st.button("Start my simulated day", type="primary"):
        commit_setup_selection()
        st.rerun()


def render_day_setup():
    profile = TEAM_PROFILES[st.session_state.team]
    st.markdown(
        f"""
        <div class="scene-stage">
          <div class="phase-pill">Simulation briefing</div>
          <h2>Your personalised day is loaded</h2>
          <p>You are entering a workday in <strong>{escape(st.session_state.team)}</strong> as <strong>{escape(st.session_state.role)}</strong>. Some choices will improve one part of the climate while creating pressure elsewhere. You will have chances to notice, repair and close the loop.</p>
          <div class="insight-grid">
            <div class="insight-card"><div class="small-label">Team purpose</div><p>{escape(profile["purpose"])}</p></div>
            <div class="insight-card"><div class="small-label">Likely pressures</div><p>{escape("; ".join(profile["pressures"][:4]))}</p></div>
            <div class="insight-card"><div class="small-label">Useful behaviours</div><p>{escape("; ".join(profile["positive_behaviours"][:4]))}</p></div>
            <div class="insight-card"><div class="small-label">Simulation frame</div><p>Every option has a trade-off. The goal is not perfection; it is noticing what becomes visible, discussable and repairable.</p></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="role-card">
          <div class="small-label">Workday map</div>
          {workday_timeline_html()}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Begin scene 1", type="primary"):
        st.session_state.stage = "simulate"
        st.rerun()


def record_open_text(scene: dict, text: str):
    if not scene.get("open_text"):
        return
    response = text.strip() if text.strip() else "No response entered."
    st.session_state.open_text_responses.append(
        {
            "scene": scene["title"],
            "prompt": scene["open_text"],
            "response": response,
        }
    )


def record_noticing(scene: dict, text: str):
    if not scene.get("noticing_pause"):
        return
    response = text.strip() if text.strip() else "No response entered."
    st.session_state.noticing_responses.append(
        {
            "scene": scene["title"],
            "prompt": scene["noticing_pause"],
            "response": response,
        }
    )


def choose_option(scene: dict, selected: dict, open_text_value: str, noticing_value: str):
    record_open_text(scene, open_text_value)
    record_noticing(scene, noticing_value)
    apply_effects(selected["effects"])
    apply_system_effects(selected.get("system_effects", {}))
    if selected.get("delayed_consequence"):
        delayed = deepcopy(selected["delayed_consequence"])
        delayed["source_scene"] = scene["title"]
        delayed["source_option"] = selected["label"]
        st.session_state.delayed_consequences.append(delayed)
    decision = {
        "time": scene["time"],
        "scene": scene["title"],
        "selected": selected["label"],
        "action": selected["action"],
        "helps": selected["helps"],
        "risk": selected["risk"],
        "unresolved": selected["unresolved"],
        "consequence": f"{selected['helps']} Risk: {selected['risk']} Still unresolved: {selected['unresolved']}",
        "tags": selected["tags"],
        "effects": selected["effects"],
        "system_effects": selected.get("system_effects", {}),
        "reaction": selected["reaction"],
        "open_text": open_text_value.strip() if open_text_value.strip() else ("No response entered." if scene.get("open_text") else ""),
        "noticing": noticing_value.strip() if noticing_value.strip() else ("No response entered." if scene.get("noticing_pause") else ""),
        "repair_scene": bool(scene.get("repair_scene")),
    }
    st.session_state.decisions.append(decision)
    st.session_state.behaviour_tags.extend(selected["tags"])
    if selected["repair"]:
        st.session_state.repair_flags.append(
            {
                "scene": scene["title"],
                "helped": selected["helps"],
                "created": selected["risk"],
                "reason": f"Earlier, your choice helped with this: {selected['helps']} It also created this risk: {selected['risk']}",
            }
        )
    if scene.get("repair_scene") and "repairing misunderstanding" in selected["tags"]:
        st.session_state.repair_flags.append(
            {"scene": scene["title"], "reason": "Repair used to restore trust and clarity."}
        )
    st.session_state.last_feedback = {
        "scene": scene["title"],
        "label": selected["label"],
        "helps": selected["helps"],
        "risk": selected["risk"],
        "unresolved": selected["unresolved"],
        "effects": selected["effects"],
        "system_effects": selected.get("system_effects", {}),
        "reaction": selected["reaction"],
        "tags": selected["tags"],
    }
    st.session_state.feedback_history.append(st.session_state.last_feedback)
    st.session_state.scene_index += 1
    if st.session_state.scene_index >= 8:
        st.session_state.final_profile = determine_profile()
        st.session_state.stage = "end"
    st.rerun()


def render_feedback():
    feedback = st.session_state.last_feedback
    if not feedback:
        return
    climate_chips = "".join(f'<span class="change-chip">{escape(k)} {v:+d} · {escape(movement_label(v, k == "Workload pressure"))}</span>' for k, v in feedback["effects"].items())
    system_chips = "".join(f'<span class="change-chip">{escape(k)} {v:+d}</span>' for k, v in feedback.get("system_effects", {}).items())
    st.markdown(
        f"""
        <div class="feedback-card">
          <div class="phase-pill">What changed after your choice</div>
          <h3>{escape(feedback["label"])}</h3>
          <div>{climate_chips}</div>
          <div>{system_chips}</div>
          <div class="insight-grid">
            <div class="insight-card"><div class="small-label">What this helped</div><p>{escape(feedback["helps"])}</p></div>
            <div class="insight-card"><div class="small-label">What risk it introduced</div><p>{escape(feedback["risk"])}</p></div>
            <div class="insight-card"><div class="small-label">What remains unresolved</div><p>{escape(feedback["unresolved"])}</p></div>
            <div class="insight-card"><div class="small-label">Behaviour practised</div><p>{tag_chips(feedback["tags"])}</p></div>
          </div>
          <div class="message-card"><div class="small-label">Stakeholder response</div><div class="message-body">{escape(feedback["reaction"])}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_card(scene: dict, selected: dict, index: int, open_text_value: str, noticing_value: str):
    st.markdown(
        f"""
        <div class="decision-card">
          <div class="decision-title">{escape(selected["label"])}</div>
          <div class="decision-meta">{escape(selected["action"])}</div>
          <div class="decision-grid">
            <div class="trade-box"><div class="small-label">Helps</div>{escape(selected["helps"])}</div>
            <div class="trade-box"><div class="small-label">Risk</div>{escape(selected["risk"])}</div>
            <div class="trade-box"><div class="small-label">Unresolved</div>{escape(selected["unresolved"])}</div>
          </div>
          <div style="margin-top:.65rem">{tag_chips(selected["tags"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"Choose this response: {selected['label']}", key=f"choose_{st.session_state.scene_index}_{index}"):
        choose_option(scene, selected, open_text_value, noticing_value)


def render_scene_object(scene: dict):
    idx = st.session_state.scene_index
    profile = TEAM_PROFILES[st.session_state.team]
    stakeholder = profile["stakeholders"][0]
    if idx in {0, 1, 5}:
        render_message_card(stakeholder, "Teams message", scene["situation"], scene["time"])
    elif idx in {2, 4}:
        render_calendar_card(scene["title"], ", ".join(profile["stakeholders"][:4]), scene["time"], system_pressure_context())
    elif idx in {3}:
        render_message_card(profile["stakeholders"][2] if len(profile["stakeholders"]) > 2 else "Cross-team colleague", "Dependency note", scene["situation"], scene["time"])
    elif idx in {6}:
        render_message_card("Colleague", "Side-channel message", scene["situation"], scene["time"])
    else:
        render_calendar_card("End-of-day reflection", st.session_state.team, scene["time"], "Close decisions, open questions and tomorrow's capacity")


def render_scene():
    scenes = build_scenes(st.session_state.team, st.session_state.role)
    maturity_warnings = validate_scenario_maturity(scenes)
    if maturity_warnings and st.query_params.get("dev") == "1":
        st.warning("Scenario maturity warnings:\n\n" + "\n".join(f"- {item}" for item in maturity_warnings))
    scene = scenes[st.session_state.scene_index]
    due = due_delayed_consequences(st.session_state.scene_index)
    st.markdown(
        f"""
        <div class="transition-card">
          <div class="small-label">Time moves to {escape(scene["time"])}</div>
          <strong>{escape(scene["title"])}</strong><br>
          {escape(SCENE_TRANSITIONS[st.session_state.scene_index])}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="scene-stage">
          <div class="phase-pill">Simulation · {escape(STATUS_LABELS[st.session_state.scene_index])}</div>
          <h2>{escape(scene["title"])}</h2>
          <p>{escape(scene["narrative"])}</p>
          <p class="muted">System pressure context: {escape(system_pressure_context())}. This can make some imperfect options feel attractive.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_scene_object(scene)

    for item in due:
        render_delayed_consequence_card(item)

    if scene.get("repair_scene"):
        if st.session_state.repair_flags:
            latest = st.session_state.repair_flags[-1]
            render_repair_window(f"{latest['reason']} You now have a chance to improve the situation.")
        else:
            render_repair_window("No major rupture is required. Repair can also mean adding clarity before confusion grows or closing a role-clarity gap before tomorrow.")

    open_text_value = ""
    if scene.get("open_text"):
        open_text_value = render_open_text_practice_card(scene["open_text"], key=f"open_text_{st.session_state.scene_index}")

    noticing_value = ""
    if scene.get("noticing_pause"):
        noticing_value = render_noticing_pause(scene["noticing_pause"], key=f"noticing_{st.session_state.scene_index}")

    st.markdown('<div class="phase-pill">Decision point</div>', unsafe_allow_html=True)
    for index, selected in enumerate(scene["options"]):
        render_decision_card(scene, selected, index, open_text_value, noticing_value)


def determine_profile() -> str:
    counts = Counter()
    for tag in st.session_state.behaviour_tags:
        counts[TAG_TO_PROFILE.get(tag, "The Practical Advocate")] += 1
    if any(d.get("repair_scene") and "repairing misunderstanding" in d["tags"] for d in st.session_state.decisions):
        counts["The Repairer"] += 2
    if st.session_state.open_text_responses:
        combined_open = " ".join(item["response"].lower() for item in st.session_state.open_text_responses)
        if any(word in combined_open for word in ["own", "owner", "deadline", "clarify", "next step"]):
            counts["The Clarifier"] += 1
        if any(word in combined_open for word in ["pause", "sorry", "moved too quickly", "repair"]):
            counts["The Repairer"] += 1
    if st.session_state.noticing_responses:
        combined_noticing = " ".join(item["response"].lower() for item in st.session_state.noticing_responses)
        if any(word in combined_noticing for word in ["hidden", "workload", "capacity", "pressure"]):
            counts["The Boundary Setter"] += 1
        if any(word in combined_noticing for word in ["voice", "heard", "included", "quiet"]):
            counts["The Inclusion Builder"] += 1
    if st.session_state.climate["Role clarity"] - CLIMATE_START["Role clarity"] >= 10:
        counts["The Clarifier"] += 1
    if CLIMATE_START["Workload pressure"] - st.session_state.climate["Workload pressure"] >= 8:
        counts["The Boundary Setter"] += 1
    if not counts:
        return "The Practical Advocate"
    return counts.most_common(1)[0][0]


def strongest_tags(limit=5) -> list[str]:
    return [tag for tag, _ in Counter(st.session_state.behaviour_tags).most_common(limit)]


def repair_summary() -> str:
    repairs_used = [d for d in st.session_state.decisions if d.get("repair_scene") and "repairing misunderstanding" in d["tags"]]
    if repairs_used:
        return "; ".join(f"{item['time']} {item['selected']}: {item['helps']}" for item in repairs_used)
    if st.session_state.repair_flags:
        return "Repair signals noticed, with at least one opportunity to respond."
    return "A generic repair opportunity was offered to strengthen clarity and trust."


def moment_of_positive_impact() -> str:
    if not st.session_state.decisions:
        return "You completed the day with reflective attention."
    best = max(st.session_state.decisions, key=lambda d: sum(v for k, v in d["effects"].items() if k != "Workload pressure") - d["effects"].get("Workload pressure", 0))
    return f"At {best['time']}, choosing '{best['selected']}' helped because: {best['consequence']}"


def alternative_moment() -> str:
    candidates = [
        d for d in st.session_state.decisions
        if any(value < 0 for key, value in d["effects"].items() if key != "Workload pressure") or d["effects"].get("Workload pressure", 0) > 0
    ]
    if not candidates:
        return "Most choices strengthened the climate; the growth edge is to keep pairing good intent with explicit ownership and sustainable work."
    d = candidates[0]
    return f"At {d['time']}, '{d['selected']}' had a trade-off: {format_effects(d['effects'])}. A different choice may have made the impact more visible earlier."


def climate_lines() -> str:
    return "\n".join(f"- {name}: {value}" for name, value in st.session_state.climate.items())


def system_pressure_lines() -> str:
    return "\n".join(f"- {name}: {value}" for name, value in st.session_state.system_pressures.items())


def open_text_lines() -> str:
    if not st.session_state.open_text_responses:
        return "- No open-text responses recorded."
    return "\n".join(
        f"- {item['scene']}: {item['response']}" for item in st.session_state.open_text_responses
    )


def noticing_lines() -> str:
    if not st.session_state.noticing_responses:
        return "- No noticing pause responses recorded."
    return "\n".join(
        f"- {item['scene']}: {item['response']}" for item in st.session_state.noticing_responses
    )


def decision_lines() -> str:
    return "\n".join(
        f"- {d['time']} {d['scene']}: {d['selected']} ({', '.join(d['tags'])})"
        for d in st.session_state.decisions
    )


def tradeoff_lines() -> str:
    if not st.session_state.decisions:
        return "- No trade-offs recorded."
    return "\n".join(
        f"- {d['scene']} / {d['selected']}: helped {d['helps'].lower()} Risk: {d['risk']}"
        for d in st.session_state.decisions
    )


def what_became_visible() -> str:
    visible = []
    if "clarifying ownership" in st.session_state.behaviour_tags:
        visible.append("ownership, decision rights and next steps")
    if "making workload visible" in st.session_state.behaviour_tags:
        visible.append("hidden workload and prioritisation trade-offs")
    if "inviting missing voices" in st.session_state.behaviour_tags:
        visible.append("perspectives that may otherwise arrive late")
    if "translating complexity" in st.session_state.behaviour_tags:
        visible.append("the practical meaning of complex constraints")
    return "; ".join(visible) if visible else "the need to keep intent, capacity and next steps visible"


def what_may_have_remained_hidden() -> str:
    hidden = []
    if st.session_state.climate["Workload pressure"] > CLIMATE_START["Workload pressure"]:
        hidden.append("some workload pressure may still be absorbed privately")
    if st.session_state.system_pressures["Ambiguity"] > SYSTEM_PRESSURE_START["Ambiguity"]:
        hidden.append("some ambiguity about ownership or scope may remain")
    if st.session_state.climate["Inclusion climate"] < CLIMATE_START["Inclusion climate"]:
        hidden.append("some voices or constraints may have arrived late")
    if st.session_state.system_pressures["Cross-team dependency"] > SYSTEM_PRESSURE_START["Cross-team dependency"]:
        hidden.append("cross-team dependencies may still need clearer handover")
    return "; ".join(hidden) if hidden else "the main remaining risk is whether the clearer signals are acted on by people with decision rights"


def generate_personal_debrief() -> str:
    team = st.session_state.team
    role = st.session_state.role
    profile = st.session_state.final_profile or determine_profile()
    details = PROFILE_DETAILS[profile]
    return dedent(
        f"""
        # Better Day personal debrief

        ## 1. Simulated role and context
        Team: {team}
        Role posture: {role}

        You moved through a simulated workday involving ambiguous requests, team interaction, cross-team dependency, workload pressure, open-text reflection and repair. {TEAM_PROFILES[team]['debrief']}

        ## 2. Pattern you tended to use
        {profile}: {details['description']}
        What this pattern contributes: {details['contributes']}
        Where it can become overused: {details['overused']}

        Behaviours demonstrated: {', '.join(strongest_tags()) or 'No behaviour tags recorded.'}

        ## 3. What became more visible
        {what_became_visible()}

        ## 4. What may have remained hidden
        {what_may_have_remained_hidden()}

        ## 5. Climate indicators at the end
        {climate_lines()}

        ## System pressures at the end
        {system_pressure_lines()}

        ## 6. One useful trade-off you managed
        {moment_of_positive_impact()}

        ## 7. One trade-off you may have under-managed
        {alternative_moment()}

        ## 8. Repair moments and what they changed
        {repair_summary()}

        ## 9. One phrase or move worth taking into real work
        {details['practice']}

        ## 10. Systemic question to raise
        {details['systemic']}

        ## Open-text responses
        {open_text_lines()}

        ## Noticing pause responses
        {noticing_lines()}
        """
    ).strip()


def generate_next_moves() -> str:
    team = st.session_state.team
    role = st.session_state.role
    profile = TEAM_PROFILES[team]
    moves = [
        f"Before accepting a new {team} request, ask: who owns the decision, what is the deadline and what can be deprioritised?",
        "When someone is quiet in a meeting, invite contribution without putting them on the spot: 'I want to check whether there is a perspective we have not heard yet.'",
        "When work expands, name the trade-off: 'I can help with this, but we need to decide what moves down the list.'",
        "When redirecting a request, explain the pathway and the reason, not just the boundary.",
        "After a tense exchange, use a repair sentence: 'I may have moved too quickly there. Can we pause and clarify what you need?'",
        f"As a {role.lower()}, connect the next step to shared purpose and one practical constraint.",
    ]
    if "data integrity" in " ".join(profile["positive_behaviours"]):
        moves[0] = "When an exception is requested, explain what is possible, what is appropriate and what protects fairness."
    if "creative" in " ".join(profile["pressures"] + profile["positive_behaviours"]):
        moves[0] = "When scope changes, name the quality, accessibility and time trade-offs before agreeing to new production work."
    return "\n".join(f"- {move}" for move in moves)


def generate_chatgpt_prompt() -> str:
    profile = st.session_state.final_profile or determine_profile()
    return dedent(
        f"""
        Act as a reflective workplace coach. I completed a workday simulation focused on positive and inclusive everyday behaviours that improve the experience of work.

        My team was {st.session_state.team}.
        My role posture was {st.session_state.role}.

        Choices made:
        {decision_lines()}

        Behaviour tags demonstrated:
        {', '.join(st.session_state.behaviour_tags) or 'No tags recorded.'}

        End climate indicators:
        {climate_lines()}

        Open-text responses:
        {open_text_lines()}

        Noticing pause responses:
        {noticing_lines()}

        System pressures:
        {system_pressure_lines()}

        Key trade-offs:
        {tradeoff_lines()}

        Repair moments:
        {repair_summary()}

        Behavioural profile:
        {profile} - {PROFILE_DETAILS[profile]['description']}

        Please identify my strengths, identify patterns in my choices, identify any possible overuse of those strengths, suggest better language for one moment, identify what systemic issue may be underneath the interpersonal moment, and suggest 3 small behaviours to practise. Avoid blame, diagnosis, moral judgement or implying that psychosocial safety is only an individual responsibility.
        """
    ).strip()


def combined_download_text() -> str:
    return "\n\n---\n\n".join(
        [
            generate_personal_debrief(),
            "# My next small moves\n\n" + generate_next_moves(),
            "# Copy-paste into Copilot (or your GenAI of choice) to prompt a reflection activity\n\n" + generate_chatgpt_prompt(),
        ]
    )


def render_timeline():
    st.markdown('<div class="phase-pill">Workday replay map</div>', unsafe_allow_html=True)
    for decision in st.session_state.decisions:
        st.markdown(
            f"""
            <div class="replay-card">
              <div class="small-label">{escape(decision["time"])} · {escape(decision["scene"])}</div>
              <h3>{escape(decision["selected"])}</h3>
              <p><strong>Key consequence:</strong> {escape(decision["helps"])} Risk: {escape(decision["risk"])} Unresolved: {escape(decision["unresolved"])}</p>
              <p>{tag_chips(decision["tags"])}</p>
              <p class="timeline-meta">Climate: {escape(format_effects(decision["effects"]))} · System: {escape(format_effects(decision.get("system_effects", {})))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if decision.get("open_text"):
            st.caption(f"Practice message: {decision['open_text']}")
        if decision.get("noticing"):
            st.caption(f"Noticing pause: {decision['noticing']}")
    for item in st.session_state.feedback_history:
        if item.get("delayed"):
            render_delayed_consequence_card(item)


def render_end():
    profile_name = st.session_state.final_profile or determine_profile()
    details = PROFILE_DETAILS[profile_name]
    st.markdown(
        f"""
        <div class="profile-card">
          <div class="phase-pill">Debrief</div>
          <h2>{escape(profile_name)}</h2>
          <p class="hero-lede">{escape(details["description"])}</p>
          <p>{tag_chips(strongest_tags())}</p>
          <div class="insight-grid">
            <div class="insight-card"><div class="small-label">What this pattern contributes</div><p>{escape(details["contributes"])}</p></div>
            <div class="insight-card"><div class="small-label">Where it can become overused</div><p>{escape(details["overused"])}</p></div>
            <div class="insight-card"><div class="small-label">Supports inclusive work by</div><p>{escape(details["inclusive"])}</p></div>
            <div class="insight-card"><div class="small-label">Systemic question</div><p>{escape(details["systemic"])}</p></div>
          </div>
          <div class="message-card"><div class="small-label">Next small move</div><div class="message-body">{escape(details["practice"])}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown('<div class="phase-pill">Final state</div>', unsafe_allow_html=True)
    end_left, end_right = st.columns(2)
    with end_left:
        render_climate_hud()
    with end_right:
        render_system_pressure_panel()
    st.markdown(
        f"""
        <div class="insight-grid">
          <div class="insight-card"><div class="small-label">What became visible</div><p>{escape(what_became_visible())}</p></div>
          <div class="insight-card"><div class="small-label">What remained unresolved</div><p>{escape(what_may_have_remained_hidden())}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_timeline()

    st.markdown('<div class="phase-pill">Reflection outputs</div>', unsafe_allow_html=True)
    with st.expander("Personal debrief", expanded=True):
        st.markdown('<div class="output-panel">', unsafe_allow_html=True)
        st.text_area("Personal debrief text", generate_personal_debrief(), height=360)
        st.markdown("</div>", unsafe_allow_html=True)
    with st.expander("My next small moves", expanded=True):
        st.text_area("Next small moves text", generate_next_moves(), height=180)
    with st.expander("Copy-paste into Copilot (or your GenAI of choice) to prompt a reflection activity", expanded=False):
        st.text_area("Reflection prompt text", generate_chatgpt_prompt(), height=360)

    st.download_button(
        "Download final debrief",
        data=combined_download_text(),
        file_name="better_day_personal_debrief.txt",
        mime="text/plain",
        type="primary",
    )
    if st.button("Start another day"):
        reset_simulation()
        st.rerun()


def main():
    init_state()
    render_css()
    render_header()

    if st.session_state.stage in {"simulate", "end"}:
        left_rail, center_stage, right_rail = st.columns([0.25, 0.50, 0.25], gap="large")
        with left_rail:
            render_role_panel()
            if st.button("Reset simulation"):
                reset_simulation()
                st.rerun()
        with center_stage:
            if st.session_state.stage == "simulate":
                render_scene()
            else:
                render_end()
        with right_rail:
            render_climate_dashboard()
            render_system_pressure_panel()
            if st.session_state.stage == "simulate":
                render_feedback()
    elif st.session_state.stage == "welcome":
        render_welcome()
    elif st.session_state.stage == "setup":
        render_setup()
    elif st.session_state.stage == "day_setup":
        render_day_setup()


if __name__ == "__main__":
    main()
