import hashlib
import html
import random
import re
import time
from datetime import date, datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Habit Flow AI",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded",
)

APP_NAME = "Habit Flow AI"
LEGACY_NAMES = ("Daily Habit & Mood Tracker AI", "Habit Flow AI AI")
USERNAME_RE = re.compile(r"[a-z0-9_.]{3,20}")
DEFAULT_PREFS = {"notify": True, "sound": False, "fx": True, "default_remind": 0}
GOAL_TYPES = {"Short-term": "🎯", "Long-term": "🏔️", "Daily habit": "🔁"}

MOODS = {
    "Happy": "😊", "Focused": "🎯", "Stressed": "😣", "Tired": "😴", "Excited": "🤩",
    "Anxious": "😟", "Motivated": "🚀", "Calm": "😌", "Lazy": "🛋️",
}

TIPS = {
    "Happy": [
        "{name}, your good mood is a free power-up. Spend it on the task you've been avoiding and watch it shrink.",
        "Great to see you smiling, {name}. Write down three things that went right today so tomorrow's you can read them.",
        "{name}, happy energy spreads. Send one kind message to someone and let it fuel your own streak.",
        "A cheerful brain learns faster, {name}. Use this window for something new, even if it's only ten minutes.",
        "Celebrate the small stuff today, {name}. Every tick you earn deserves a proper little victory dance.",
        "{name}, notice what made you feel good this morning. Habits stick best when they're tied to things you enjoy.",
        "Ride the wave, {name}. Do your hardest goal first while confidence is high, then reward yourself.",
        "You're glowing today, {name}. Take a minute to plan tomorrow's top goal so this mood carries forward.",
        "{name}, happiness plus action equals momentum. Pick one goal and give it your first twenty minutes.",
        "Smiles are contagious, {name}. Work or study alongside a friend today and make it fun.",
        "Gratitude locks in good days, {name}. Name one thing you're thankful for before your first task.",
        "{name}, you don't need a perfect day to build a habit, just a good one like this. Make it count.",
    ],
    "Focused": [
        "You're in the zone, {name}. Silence notifications for 25 minutes and give your goal your full attention.",
        "{name}, one task at a time wins. Close the extra tabs and finish the current thing before opening the next.",
        "Deep focus is rare, {name}. Protect it by keeping water and notes within reach so you never have to stop.",
        "Nice concentration, {name}. After this sprint, take a proper five-minute break so your focus lasts all day.",
        "{name}, write the very next action on a sticky note. When distractions pop up, you'll know where to return.",
        "Use your sharp mind on the hardest part first, {name}. Everything else will feel lighter afterward.",
        "{name}, set a timer and race it. A visible countdown keeps a focused mind honest.",
        "Keep going, {name}. Park stray ideas on a 'later' list so they stop competing for your attention.",
        "Focus is a muscle, {name}, and today it's strong. Note what helped so you can recreate it.",
        "{name}, break big goals into checklists. Each tick feeds your focus with a small win.",
        "Stay in flow, {name}. If you hit a wall, switch to a smaller related task instead of switching apps.",
        "Brilliant work, {name}. Finish with a two-line summary of what you did so tomorrow starts smoothly.",
    ],
    "Stressed": [
        "Breathe in for four, out for six, {name}. Three rounds can calm your whole body before you start.",
        "{name}, you can't do everything at once. Pick the single most important thing and let the rest wait.",
        "Stress means you care, {name}. Turn that care into a five-minute first step and begin right now.",
        "Step away from the screen for two minutes, {name}. A glass of water and a stretch can reset your thinking.",
        "{name}, write every worry on paper, then circle only the ones you can act on today.",
        "Be gentle with yourself today, {name}. Done and imperfect beats perfect and never started.",
        "{name}, shrink your list. Three realistic tasks are better than ten you dread.",
        "Try the 5-4-3-2-1 trick, {name}: name five things you see, four you feel, three you hear, two you smell, one you taste.",
        "Pressure is temporary, {name}. Take a short walk, then come back and handle one small piece.",
        "{name}, ask for help if something feels too big. Sharing the load is smart strategy, not weakness.",
        "Drop your shoulders and unclench your jaw, {name}. Relaxing your body tells your mind it's safe to focus.",
        "You've handled hard days before, {name}. Remember one of them and carry that proof into this task.",
    ],
    "Tired": [
        "Go gently today, {name}. Ten easy minutes on your goal still count as progress.",
        "{name}, rest is part of the plan. Drink water, stretch, then do the smallest version of your habit.",
        "Low energy happens to everyone, {name}. Start with the easiest task and let momentum wake you up.",
        "Be kind to yourself, {name}. Protect tonight's sleep and tomorrow will feel lighter.",
        "{name}, try a ten-minute walk in daylight. It often beats another coffee for tiredness.",
        "When energy is low, {name}, lower the bar instead of quitting. Do half the usual and call it a win.",
        "A twenty-minute nap can refresh you, {name}. Set an alarm so it helps rather than hurts.",
        "{name}, eat something with protein and drink some water. Your brain may simply need fuel.",
        "Tired days suit tidy tasks, {name}. Sort, organise or plan instead of forcing deep work.",
        "{name}, swap screens for stretching for five minutes. Your eyes and shoulders will thank you.",
        "You showed up even while tired, {name}, and that's what builds strong habits. Be proud of it.",
        "{name}, put your phone away an hour before bed tonight. Better rest is the best productivity hack.",
    ],
    "Excited": [
        "{name}, that excitement is rocket fuel. Aim it at a clear first step before it fades.",
        "Love the energy, {name}. Write your big idea down now so none of it slips away.",
        "{name}, point all that enthusiasm at one goal first. Finishing one thing beats starting five.",
        "Exciting days deserve a plan, {name}. Spend five minutes mapping the steps toward what you're looking forward to.",
        "Share your good news, {name}. Telling someone your goal makes you more likely to follow through.",
        "{name}, use this buzz to start the task you usually postpone. Excitement makes beginnings easy.",
        "Keep your pace steady, {name}. A short breathing pause between tasks stops excitement turning into scatter.",
        "{name}, capture this feeling in one sentence. Re-read it when motivation dips later.",
        "Big feelings make great momentum, {name}. Set a 30-minute timer and go all in.",
        "{name}, turn today's excitement into a streak. Take one tiny action every day this week and watch it grow.",
        "Great energy, {name}. Remember to eat and drink water so it lasts the whole day.",
        "{name}, celebrate when you finish your task. Pairing effort with fun trains your brain to want more.",
    ],
    "Anxious": [
        "Place a hand on your chest and take three slow breaths, {name}. Then take just one small step.",
        "{name}, anxious thoughts love 'what if'. Ask 'what's one thing I can do right now?' instead.",
        "Break it down, {name}. The first step should feel almost silly, like simply opening the notebook.",
        "{name}, write the worry down and give it a time slot later today. Right now, give your task ten minutes.",
        "Ground yourself, {name}: feel your feet on the floor and name three things you can see around you.",
        "Feeling nervous doesn't mean you're unprepared, {name}. It means this matters to you.",
        "{name}, make your exhales longer than your inhales. It tells your body the alarm can ease off.",
        "Talk to someone you trust today, {name}. Saying worries out loud makes them smaller.",
        "{name}, focus on effort rather than outcome. Your only job right now is to try your best at the next step.",
        "Keep your routine steady, {name}. Familiar habits work like an anchor when thoughts feel stormy.",
        "{name}, limit news and social media for an hour. A quieter feed can mean a quieter mind.",
        "You've felt this before and moved through it, {name}. If worry feels heavy for days, talk to a counsellor or doctor.",
    ],
    "Motivated": [
        "You're on fire, {name}. Pick the biggest goal on your list and take the first bold step now.",
        "{name}, motivation is great but systems last. Attach your goal to a fixed time and place today.",
        "Strike while it's hot, {name}. Do your hardest task first and enjoy the rest of the day.",
        "{name}, write down why this goal matters to you. Future-you will want that reminder on tougher days.",
        "Set a clear target for today, {name}. 'Finish chapter 3' beats 'study more' every time.",
        "{name}, your drive is contagious. Invite a friend to join your habit and keep each other going.",
        "Use this energy to prepare for tomorrow too, {name}. Lay out what you need tonight.",
        "{name}, track every tick today. Seeing progress stack up keeps motivation alive after the spark fades.",
        "Go beyond the minimum, {name}, but stop before you burn out. Consistency beats intensity.",
        "{name}, reward yourself after each finished goal. Small treats make hard work something to look forward to.",
        "You're building something, {name}. Every day you show up adds another brick to your streak.",
        "{name}, ride this motivation to set one goal for the next seven days while you feel unstoppable.",
    ],
    "Calm": [
        "A peaceful mind is a productive one, {name}. Choose one meaningful goal and do it slowly and well.",
        "{name}, use this steady mood for reflection. Write three lines about what's working in your routine.",
        "Calm is perfect for planning, {name}. Map out your week and give each goal a day.",
        "{name}, enjoy the quiet. Work without rushing and notice how good careful effort feels.",
        "Your calm helps you think clearly, {name}. Tackle the task that needs patience and detail.",
        "{name}, add a mindful minute to today: breathe, notice your surroundings, then start.",
        "A relaxed pace can still make progress, {name}. Finish one goal fully before you begin another.",
        "{name}, tidy your space for five minutes. A clear desk helps a calm mind stay calm.",
        "Good time for gentle learning, {name}. Fifteen quiet pages add up faster than you'd think.",
        "{name}, journal your intentions for tomorrow. Calm evenings make bright mornings.",
        "Balanced days build lasting habits, {name}. Keep today steady and don't chase extremes.",
        "{name}, share your calm. A kind word to someone who's stressed can lift you both.",
    ],
    "Lazy": [
        "Lazy days happen, {name}. Promise yourself just two minutes of your goal and see if you keep going.",
        "{name}, start before you feel ready. Open the book or the file, and the hardest part is done.",
        "Make it easy, {name}: put your goal materials where you can see them and lower the barrier to starting.",
        "{name}, pick your tiniest task and finish it. A quick win breaks the lazy spell.",
        "Try the five-minute rule, {name}: work for five minutes, then decide if you want to stop. You rarely will.",
        "{name}, change your spot. A new corner or a short walk can wake up a sleepy routine.",
        "Pair your task with a treat, {name}: your favourite music or a snack while you work.",
        "It's okay to move slowly, {name}, as long as you keep moving. One small tick keeps the streak alive.",
        "{name}, stand up, stretch and drink some water. Movement is the quickest cure for the lazies.",
        "Ask yourself, {name}: what's the easiest version of this goal? Do that today and call it a win.",
        "{name}, tell a friend what you'll do in the next hour. A little accountability beats willpower.",
        "Lazy now doesn't mean lazy forever, {name}. Today's tiny action is a vote for the person you want to become.",
    ],
}

NUDGES = {
    "Short-term": [
        "break it into two or three steps and finish the first one before the day ends.",
        "set a 25-minute timer and work on it without switching tasks.",
        "decide exactly when you'll start, then treat that time like an appointment.",
    ],
    "Long-term": [
        "choose one tiny action today that moves it forward, because big goals grow from daily steps.",
        "write down the next milestone and put a date on it.",
        "think of today as one brick in the wall, and lay it before you rest.",
    ],
    "Daily habit": [
        "link it to something you already do, like after breakfast, so it becomes automatic.",
        "keep it small enough that you can't say no, and never skip two days in a row.",
        "tick it off as early as you can so the day doesn't get away from you.",
    ],
}

TOUR = [
    ("hero", "Welcome aboard!", "I'm your quest guide. Follow the glowing spots to learn the places you'll use every day."),
    ("sec_goals", "Click here to set your goal", "Type what you want to achieve, pick short-term, long-term or daily habit, add an optional reminder, then press Add goal."),
    ("sec_reminders", "Your reminders live here", "Goals with a reminder get a live countdown. Tap +5 min if you need a little more time."),
    ("sec_mood", "Select your mood here", "Choose how you feel, optionally pick a goal, then press Get AI Tip for advice made for you."),
    ("sec_history", "Your progress is saved here", "Completed goals and every tip you receive are kept here for the whole session."),
    ("sidebar", "Change settings in the sidebar", "Rename the app, switch dark or light mode, set reminders and sound, or reset your data."),
]

THEMES = {
    "light": {
        "scheme": "light",
        "bg": "radial-gradient(900px 560px at 6% -8%, #BDEBE2 0%, transparent 60%), radial-gradient(800px 560px at 100% 100%, #FFE2B5 0%, transparent 58%), linear-gradient(160deg, #EEF6F4, #E5EDF8)",
        "side": "rgba(255,255,255,.74)", "text": "#12312C", "muted": "#4A625D",
        "card": "rgba(255,255,255,.68)", "border": "rgba(255,255,255,.9)", "border_strong": "#B7CBC6",
        "input": "#FFFFFF", "input_text": "#0F172A", "input_border": "#94A3B8", "chip": "rgba(15,118,110,.10)", "accent": "#0F766E", "glow": "rgba(15,118,110,.45)",
        "shadow": "0 16px 38px rgba(20,70,65,.16), inset 0 1px 0 rgba(255,255,255,.95)",
        "shadow_hover": "0 24px 52px rgba(20,70,65,.24), inset 0 1px 0 rgba(255,255,255,.95)",
        "late": "#B91C1C",
    },
    "dark": {
        "scheme": "dark",
        "bg": "radial-gradient(900px 560px at 6% -8%, #0E4A47 0%, transparent 60%), radial-gradient(800px 560px at 100% 100%, #1E2F6B 0%, transparent 58%), linear-gradient(160deg, #09101F, #0F1A30)",
        "side": "rgba(10,16,32,.82)", "text": "#E7F2F0", "muted": "#9FB5B1",
        "card": "rgba(20,31,52,.66)", "border": "rgba(255,255,255,.11)", "border_strong": "rgba(255,255,255,.24)",
        "input": "#0E1830", "input_text": "#E7F2F0", "input_border": "rgba(255,255,255,.28)", "chip": "rgba(45,212,191,.12)", "accent": "#2DD4BF", "glow": "rgba(45,212,191,.5)",
        "shadow": "0 18px 44px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.08)",
        "shadow_hover": "0 26px 58px rgba(0,0,0,.68), inset 0 1px 0 rgba(255,255,255,.12)",
        "late": "#FCA5A5",
    },
}

FONT_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');"

BASE_CSS = """
html, body, .stApp, button, input, textarea, label { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
.stApp { background: var(--bg); background-attachment: fixed; color: var(--text); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"], .block-container { max-width: 940px !important; padding-top: 2rem; }
[data-testid="stSidebar"] { background: var(--side); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border-right: 1px solid var(--border); }

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp li, .stApp label, .stApp summary,
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] { color: var(--text); }
.stApp ::placeholder { color: var(--muted); opacity: .85; }

.stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"], .stApp [data-baseweb="textarea"],
.stApp [data-testid="stTextInputRootElement"], .stApp [data-testid="stNumberInputContainer"],
.stApp [data-baseweb="select"] > div, .stApp .stTextArea textarea {
    background-color: var(--input) !important; background-image: none !important;
    border-color: var(--input-border) !important; border-radius: 12px !important;
}
.stApp [data-baseweb="input"], .stApp [data-baseweb="select"] > div { border: 1px solid var(--input-border) !important; }
.stApp input, .stApp textarea, .stApp [data-baseweb="input"] input, .stApp [data-baseweb="base-input"] input,
.stApp [data-testid="stTextInput"] input, .stApp [data-testid="stNumberInput"] input {
    background: var(--input) !important; background-color: var(--input) !important;
    color: var(--input-text) !important; -webkit-text-fill-color: var(--input-text) !important;
    caret-color: var(--input-text) !important; opacity: 1 !important;
}
.stApp input::placeholder, .stApp textarea::placeholder { color: var(--muted) !important; -webkit-text-fill-color: var(--muted) !important; opacity: 1 !important; }
.stApp input:-webkit-autofill, .stApp input:-webkit-autofill:hover, .stApp input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px var(--input) inset !important; -webkit-text-fill-color: var(--input-text) !important;
}
.stApp [data-baseweb="input"] button { background: transparent !important; color: var(--input-text) !important; }
.stApp [data-baseweb="input"] svg { fill: var(--input-text) !important; }
.stApp [data-baseweb="select"] * { color: var(--input-text) !important; }
.stApp [data-baseweb="select"] svg { fill: var(--input-text) !important; }
div[data-baseweb="popover"] > div, ul[role="listbox"] { background: var(--input) !important; }
ul[role="listbox"] li { color: var(--input-text) !important; }
ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"] { background: var(--chip) !important; }
[data-testid="stNumberInput"] button { background: var(--input) !important; color: var(--input-text) !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--glow) !important;
}
[data-testid="stForm"] { border: 1px solid var(--border-strong); border-radius: 18px; background: var(--chip); }
[data-testid="stExpander"] { background: var(--chip); border: 1px solid var(--border-strong); border-radius: 14px; }
[data-testid="stExpander"] summary svg { color: var(--text); fill: var(--text); }
.stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--border-strong); }
.stTabs [data-baseweb="tab"] p { color: var(--muted) !important; font-weight: 700; }
.stTabs [aria-selected="true"] p { color: var(--accent) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--accent) !important; }

.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(135deg, #0F766E, #1D4ED8); color: #FFFFFF; border: none; border-radius: 14px;
    padding: .6rem 1.4rem; font-weight: 700;
    box-shadow: 0 5px 0 #0B3B6B, 0 12px 22px rgba(15,60,120,.35);
    transition: transform .15s ease, box-shadow .15s ease, filter .2s ease;
}
.stButton > button p, .stFormSubmitButton > button p { color: #FFFFFF !important; }
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-2px); filter: brightness(1.1); box-shadow: 0 7px 0 #0B3B6B, 0 16px 26px rgba(15,60,120,.4);
}
.stButton > button:active, .stFormSubmitButton > button:active { transform: translateY(4px); box-shadow: 0 1px 0 #0B3B6B, 0 4px 10px rgba(15,60,120,.35); }
.stButton > button:focus-visible, .stFormSubmitButton > button:focus-visible { outline: 3px solid #FBBF24; outline-offset: 3px; }
.stButton > button:disabled { opacity: .5; transform: none; box-shadow: none; cursor: not-allowed; }
[data-testid="stSidebar"] .stButton > button { width: 100%; }
[class*="st-key-del_"] button, [class*="st-key-snz_"] button {
    background: var(--chip); border: 1px solid var(--border-strong); padding: .4rem .8rem;
    box-shadow: 0 3px 0 var(--border-strong); filter: none;
}
[class*="st-key-del_"] button p, [class*="st-key-snz_"] button p { color: var(--text) !important; }

.st-key-acct_delete button { background: linear-gradient(135deg, #B91C1C, #7F1D1D); box-shadow: 0 5px 0 #450A0A, 0 12px 22px rgba(127,29,29,.35); }
.st-key-acct_delete button:hover { box-shadow: 0 7px 0 #450A0A, 0 16px 26px rgba(127,29,29,.45); }

[class*="st-key-sec_"] {
    background: var(--card); backdrop-filter: blur(16px) saturate(1.3); -webkit-backdrop-filter: blur(16px) saturate(1.3);
    border: 1px solid var(--border); border-radius: 24px; padding: 1.3rem 1.5rem; margin-bottom: 1.1rem;
    box-shadow: var(--shadow); transition: transform .35s ease, box-shadow .35s ease;
}
[class*="st-key-sec_"]:hover { transform: translateY(-4px); box-shadow: var(--shadow-hover); }
[class*="st-key-goal_"] {
    background: var(--chip); border: 1px solid var(--border-strong); border-radius: 16px; padding: .6rem .9rem;
    transition: transform .25s ease, box-shadow .25s ease;
}
[class*="st-key-goal_"]:hover { transform: translateX(4px) translateY(-2px); box-shadow: 0 10px 22px rgba(0,0,0,.12); }

.hf-hero {
    position: relative; overflow: hidden; border-radius: 26px; padding: 1.8rem 2rem; margin-bottom: 1.2rem; color: #FFFFFF;
    background: linear-gradient(135deg, #0F766E 0%, #1D4ED8 100%);
    box-shadow: 0 22px 44px rgba(20,60,130,.35), inset 0 2px 0 rgba(255,255,255,.35), inset 0 -6px 0 rgba(0,0,0,.18);
    transform: perspective(1100px) rotateX(3deg); transition: transform .4s ease;
}
.hf-hero:hover { transform: perspective(1100px) rotateX(0deg) translateY(-3px); }
.hf-hero .hf-date { font-weight: 600; font-size: .9rem; opacity: .92; }
.hf-hero .hf-title { font-size: 2.1rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.15; margin: .25rem 0; }
.hf-hero .hf-sub { font-size: 1.05rem; max-width: 34rem; }
.hf-orb { position: absolute; border-radius: 50%; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.55), rgba(255,255,255,.04)); animation: floaty 6s ease-in-out infinite; }

.hf-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: .9rem; margin-bottom: 1.2rem; }
.hf-stat { background: var(--card); border: 1px solid var(--border); border-radius: 18px; padding: .9rem 1rem; text-align: center; box-shadow: var(--shadow); transition: transform .3s ease; }
.hf-stat:hover { transform: translateY(-5px) rotateX(6deg); }
.hf-stat b { display: block; font-size: 1.7rem; color: var(--accent); }
.hf-stat span { color: var(--muted); font-size: .82rem; font-weight: 600; }
@media (max-width: 640px) { .hf-stats { grid-template-columns: repeat(2, 1fr); } .hf-hero .hf-title { font-size: 1.6rem; } }

.hf-sec-title { font-weight: 800; font-size: 1.25rem; color: var(--text); }
.hf-sec-sub { color: var(--muted); font-size: .92rem; margin-bottom: .9rem; }
.hf-barwrap { margin: .4rem 0 .9rem; }
.hf-barlabel { display: flex; justify-content: space-between; color: var(--muted); font-weight: 600; font-size: .85rem; margin-bottom: .3rem; }
.hf-bar { height: 14px; border-radius: 999px; background: var(--chip); box-shadow: inset 0 2px 5px rgba(0,0,0,.2); overflow: hidden; }
.hf-bar i { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #14B8A6, #3B82F6); box-shadow: 0 0 12px var(--glow); transition: width .6s ease; }

.hf-metarow { display: flex; flex-wrap: wrap; gap: .5rem; margin: -.1rem 0 .3rem 1.8rem; align-items: center; }
.hf-badge { background: var(--chip); border: 1px solid var(--accent); color: var(--text); font-weight: 700; font-size: .78rem; padding: .12rem .6rem; border-radius: 999px; }
.hf-meta { color: var(--muted); font-size: .8rem; font-weight: 600; }
.hf-meta.ok { color: var(--accent); }
.hf-empty { text-align: center; color: var(--muted); padding: 1.2rem; border: 2px dashed var(--border-strong); border-radius: 16px; font-weight: 600; }

.hf-rem { background: var(--chip); border: 1px solid var(--border-strong); border-radius: 16px; padding: .8rem 1rem; margin-bottom: .4rem; }
.hf-rem-top { display: flex; justify-content: space-between; gap: 1rem; font-weight: 700; color: var(--text); margin-bottom: .5rem; }
.hf-time { font-variant-numeric: tabular-nums; color: var(--accent); font-weight: 800; }
.hf-rem.late .hf-time { color: var(--late); animation: blink 1s ease-in-out infinite; }

.hf-tipcard { background: var(--card); border: 1px solid var(--border-strong); border-left: 8px solid var(--accent); border-radius: 20px; padding: 1.2rem 1.4rem; margin-top: 1rem; box-shadow: var(--shadow); animation: popin .55s cubic-bezier(.2,1.4,.4,1); }
.hf-tipmood { display: inline-block; background: var(--chip); border: 1px solid var(--accent); color: var(--text); font-weight: 700; font-size: .85rem; padding: .2rem .8rem; border-radius: 999px; margin-bottom: .7rem; }
.hf-tiptext { font-size: 1.15rem; line-height: 1.6; font-weight: 600; color: var(--text); }
.hf-tipfoot { color: var(--muted); font-size: .85rem; margin-top: .8rem; }

.hf-row { display: flex; gap: .8rem; align-items: flex-start; padding: .7rem .2rem; border-bottom: 1px solid var(--border-strong); }
.hf-check { flex: none; width: 26px; height: 26px; border-radius: 50%; background: linear-gradient(135deg, #14B8A6, #1D4ED8); color: #FFFFFF; font-weight: 800; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 0 #0B3B6B; }
.hf-rt { color: var(--text); font-weight: 700; }
.hf-rm { color: var(--muted); font-size: .82rem; margin-top: .1rem; }

.hf-tour { border-radius: 20px; padding: 1.1rem 1.4rem; margin-bottom: 1rem; color: #FFFFFF; background: linear-gradient(135deg, #111827, #0F766E); border: 2px solid #FBBF24; box-shadow: 0 0 0 4px rgba(251,191,36,.25), 0 18px 36px rgba(0,0,0,.35); }
.hf-tour .hf-step { color: #FDE68A; font-weight: 800; font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; }
.hf-tour .hf-ttl { font-size: 1.3rem; font-weight: 800; margin: .2rem 0; }
.hf-dots { display: flex; gap: .4rem; margin-top: .7rem; }
.hf-dots span { width: 10px; height: 10px; border-radius: 50%; background: rgba(255,255,255,.3); }
.hf-dots span.on { background: #FBBF24; }
.hf-pointer { display: inline-block; background: #FBBF24; color: #1F2937; font-weight: 800; padding: .35rem .9rem; border-radius: 999px; margin-bottom: .7rem; box-shadow: 0 5px 0 #B45309; animation: bob 1s ease-in-out infinite; }

.hf-side-brand { font-weight: 800; font-size: 1.15rem; color: var(--text); }
.hf-side-user { color: var(--muted); font-size: .85rem; margin-bottom: .6rem; }
.hf-side-h { font-weight: 800; color: var(--accent); font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; margin: .8rem 0 .3rem; }
.hf-note { background: var(--card); border: 1px solid var(--border-strong); border-left: 6px solid #DC2626; border-radius: 12px; padding: .6rem .9rem; color: var(--text); font-weight: 600; margin-top: .6rem; }
.hf-note.good { border-left-color: var(--accent); }

@keyframes floaty { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-14px); } }
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes blink { 50% { opacity: .45; } }
@keyframes popin { from { opacity: 0; transform: translateY(14px) scale(.93); } to { opacity: 1; transform: none; } }
@keyframes tourGlow { 0%, 100% { box-shadow: 0 0 0 0 rgba(251,191,36,0), var(--shadow); } 50% { box-shadow: 0 0 36px 10px rgba(251,191,36,.6), var(--shadow); } }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
"""

CONFETTI_CSS = (
    "@keyframes cfA__ID__{0%{transform:translate3d(0,-12vh,0) rotate(0)}100%{transform:translate3d(60px,108vh,0) rotate(720deg)}}"
    "@keyframes cfB__ID__{0%{transform:translate3d(0,-12vh,0) rotate(0)}100%{transform:translate3d(-60px,108vh,0) rotate(-720deg)}}"
    ".hf-confetti{position:fixed;inset:0;pointer-events:none;z-index:99999;overflow:hidden}"
    ".hf-confetti i{position:absolute;top:0;display:block;animation-timing-function:cubic-bezier(.3,.6,.5,1);animation-fill-mode:both}"
    ".hf-confetti i.a{animation-name:cfA__ID__}.hf-confetti i.b{animation-name:cfB__ID__}"
)
CONFETTI_COLORS = ["#F59E0B", "#14B8A6", "#3B82F6", "#EC4899", "#22C55E", "#EF4444", "#A855F7", "#FACC15"]

BEEP = """<script>
try {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const t = ctx.currentTime;
  [[660, 0], [880, .16], [1175, .32]].forEach(([f, d]) => {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = 'sine'; o.frequency.value = f;
    g.gain.setValueAtTime(.0001, t + d);
    g.gain.exponentialRampToValueAtTime(.2, t + d + .02);
    g.gain.exponentialRampToValueAtTime(.0001, t + d + .25);
    o.connect(g); g.connect(ctx.destination);
    o.start(t + d); o.stop(t + d + .3);
  });
} catch (e) {}
</script>"""


# ---------------------------------------------------------------- helpers
def esc(value):
    return html.escape(str(value))


def me():
    return st.session_state.users[st.session_state.user]


def fmt_ts(ts):
    return datetime.fromtimestamp(ts).strftime("%d %b, %I:%M %p")


def fmt_clock(seconds):
    s = int(max(seconds, 0))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


def greeting():
    hour = datetime.now().hour
    return "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"


def hash_pw(username, password):
    return hashlib.sha256(f"{username}:{password}".encode()).hexdigest()


def new_user(username, name, password):
    return {
        "pw": hash_pw(username, password), "name": name, "app_name": APP_NAME,
        "goals": [], "tips": [], "next_id": 1, "toured": False,
        "prefs": dict(DEFAULT_PREFS), "joined": time.time(),
    }


def build_css(dark, target):
    theme = dict(THEMES["dark" if dark else "light"])
    scheme = theme.pop("scheme")
    root = ":root{color-scheme:" + scheme + ";" + "".join(f"--{k.replace('_', '-')}:{v};" for k, v in theme.items()) + "}"
    glow = ""
    if target:
        sel = {"sidebar": '[data-testid="stSidebar"]', "hero": ".hf-hero"}.get(target, f".st-key-{target}")
        glow = sel + "{outline:3px solid #FBBF24 !important;outline-offset:4px;animation:tourGlow 1.3s ease-in-out infinite !important;}"
    return "<style>" + FONT_IMPORT + root + BASE_CSS + glow + "</style>"


def confetti_markup(n):
    pieces = []
    for _ in range(70):
        size = random.uniform(6, 12)
        radius = "50%" if random.random() < 0.35 else "2px"
        pieces.append(
            f'<i class="{random.choice("ab")}" style="left:{random.uniform(0, 100):.1f}vw;width:{size:.0f}px;'
            f'height:{size * 1.4:.0f}px;background:{random.choice(CONFETTI_COLORS)};border-radius:{radius};'
            f'animation-delay:{random.uniform(0, .8):.2f}s;animation-duration:{random.uniform(2.2, 3.8):.2f}s"></i>'
        )
    css = CONFETTI_CSS.replace("__ID__", str(n))
    return f'<style>{css}</style><div class="hf-confetti">{"".join(pieces)}</div>'


def bar_html(pct, label):
    return (f'<div class="hf-barwrap"><div class="hf-barlabel"><span>{esc(label)}</span><span>{pct}%</span></div>'
            f'<div class="hf-bar"><i style="width:{pct}%"></i></div></div>')


def section_head(title, sub):
    st.markdown(f'<div class="hf-sec-title">{title}</div><div class="hf-sec-sub">{esc(sub)}</div>', unsafe_allow_html=True)


def pointer(target):
    step = st.session_state.get("tour_step")
    if step is not None and TOUR[step][0] == target:
        st.markdown(f'<div class="hf-pointer">👉 {esc(TOUR[step][1])}</div>', unsafe_allow_html=True)


def find_goal(gid):
    return next((g for g in me()["goals"] if g["id"] == gid), None)


def queue_fx():
    st.session_state.fx_pending = True


def streak_days(goals):
    days = {datetime.fromtimestamp(g["done_at"]).date() for g in goals if g["done"] and g["done_at"]}
    day = date.today()
    if day not in days:
        day -= timedelta(days=1)
    count = 0
    while day in days:
        count += 1
        day -= timedelta(days=1)
    return count


# -------------------------------------------------------------- callbacks
def set_theme(key):
    st.session_state.dark = st.session_state[key]


def set_pref(name, key):
    me()["prefs"][name] = st.session_state[key]


def save_settings():
    u = me()
    u["app_name"] = st.session_state.get("set_app", "").strip() or APP_NAME
    u["name"] = st.session_state.get("set_name", "").strip() or u["name"]
    st.session_state.flash = "💾 Settings saved"


def submit_goal():
    title = st.session_state.get("new_title", "").strip()
    if not title:
        st.session_state.flash = "✏️ Type a goal first"
        return
    u = me()
    now = time.time()
    minutes = int(st.session_state.get("new_mins", 0) or 0)
    u["goals"].append({
        "id": u["next_id"], "title": title[:120], "type": st.session_state.get("new_type", "Short-term"),
        "created": now, "start": now, "due": now + minutes * 60 if minutes else None,
        "done": False, "done_at": None, "notified": False,
    })
    u["next_id"] += 1
    st.session_state.flash = "🎯 Goal added"


def toggle_goal(gid):
    g = find_goal(gid)
    if not g:
        return
    g["done"] = bool(st.session_state.get(f"chk_{gid}", False))
    g["done_at"] = time.time() if g["done"] else None
    if g["done"]:
        queue_fx()
        st.session_state.flash = "🎉 Goal completed. Great work!"


def delete_goal(gid):
    u = me()
    u["goals"] = [g for g in u["goals"] if g["id"] != gid]


def snooze(gid):
    g = find_goal(gid)
    if not g:
        return
    now = time.time()
    if g["due"] <= now:
        g["start"], g["due"] = now, now + 300
    else:
        g["due"] += 300
    g["notified"] = False


def give_tip():
    u = me()
    mood = st.session_state.get("mood_pick", "Happy")
    goal = find_goal(st.session_state.get("focus_pick", 0))
    pool = TIPS[mood]
    recent = {t["idx"] for t in u["tips"][-8:] if t["mood"] == mood}
    choices = [i for i in range(len(pool)) if i not in recent] or list(range(len(pool)))
    idx = random.choice(choices)
    text = pool[idx].format(name=u["name"])
    if goal:
        text += f" For “{goal['title']}”, " + random.choice(NUDGES.get(goal["type"], NUDGES["Short-term"]))
    u["tips"].append({"ts": time.time(), "mood": mood, "idx": idx, "text": text, "goal": goal["title"] if goal else None})
    queue_fx()
    st.session_state.flash = "✨ New tip ready"


def clear_done():
    u = me()
    u["goals"] = [g for g in u["goals"] if not g["done"]]
    st.session_state.flash = "🧹 Completed goals cleared"


def clear_tips():
    me()["tips"] = []
    st.session_state.flash = "🧹 Tip history cleared"


def reset_all():
    u = me()
    u["goals"], u["tips"], u["next_id"] = [], [], 1
    u["prefs"] = dict(DEFAULT_PREFS)
    for key, val in (("pf_notify", True), ("pf_sound", False), ("pf_fx", True), ("pf_remind", 0), ("rs_confirm", False)):
        st.session_state[key] = val
    st.session_state.flash = "♻️ All data reset"


def change_username():
    ss = st.session_state
    old, u = ss.user, me()
    new = ss.get("acc_new_user", "").strip().lower()
    if u["pw"] != hash_pw(old, ss.get("acc_user_pw", "")):
        ss.flash = "⚠️ Current password is incorrect"
    elif not USERNAME_RE.fullmatch(new):
        ss.flash = "⚠️ Username needs 3-20 letters, numbers, dots or underscores"
    elif new == old:
        ss.flash = "⚠️ That is already your username"
    elif new in ss.users:
        ss.flash = "⚠️ That username is taken"
    else:
        ss.users[new] = ss.users.pop(old)
        ss.users[new]["pw"] = hash_pw(new, ss.acc_user_pw)
        ss.user = new
        ss.flash = f"✅ Username changed to @{new}"


def change_password():
    ss = st.session_state
    u = me()
    if u["pw"] != hash_pw(ss.user, ss.get("pw_cur", "")):
        ss.flash = "⚠️ Current password is incorrect"
    elif len(ss.get("pw_new", "")) < 4:
        ss.flash = "⚠️ New password needs at least 4 characters"
    elif ss.pw_new != ss.get("pw_conf", ""):
        ss.flash = "⚠️ The new passwords don't match"
    else:
        u["pw"] = hash_pw(ss.user, ss.pw_new)
        ss.flash = "🔑 Password updated"


def delete_account():
    ss = st.session_state
    if me()["pw"] != hash_pw(ss.user, ss.get("acct_pw", "")):
        ss.flash = "⚠️ Password is incorrect. Account not deleted"
        return
    ss.users.pop(ss.user, None)
    for key in list(ss.keys()):
        if key not in ("users", "dark", "fx_n"):
            del ss[key]
    ss.user = None
    ss.tour_step = None
    ss.flash = "🗑️ Account deleted. Log in or sign up whenever you like"


def logout():
    st.session_state.user = None
    st.session_state.tour_step = None


def tour_end(finished):
    me()["toured"] = True
    st.session_state.tour_step = None
    if finished:
        queue_fx()
        st.session_state.flash = "🏆 Tour complete. You're ready to go!"


def tour_move(delta):
    step = st.session_state.tour_step + delta
    if step >= len(TOUR):
        tour_end(True)
    else:
        st.session_state.tour_step = max(0, step)


def replay_tour():
    st.session_state.tour_step = 0


# ------------------------------------------------------------------ pages
def auth_screen():
    flash = st.session_state.pop("flash", None)
    if flash:
        st.toast(flash)
    st.toggle("🌙 Dark mode", value=st.session_state.dark, key="dark_toggle_auth",
              on_change=set_theme, args=("dark_toggle_auth",))
    st.markdown(
        f'<div class="hf-hero"><span class="hf-orb" style="width:130px;height:130px;right:-30px;top:-34px"></span>'
        f'<span class="hf-orb" style="width:70px;height:70px;right:130px;bottom:-24px;animation-delay:-2s"></span>'
        f'<div class="hf-date">Welcome</div><div class="hf-title">{esc(APP_NAME)}</div>'
        f'<div class="hf-sub">Log in or create an account to set goals, track your mood and get tips made for you.</div></div>',
        unsafe_allow_html=True,
    )
    tab_in, tab_up = st.tabs(["🔐 Log in", "✨ Sign up"])
    users = st.session_state.users
    with tab_in:
        with st.form("login_form"):
            username = st.text_input("Username", key="li_user")
            password = st.text_input("Password", type="password", key="li_pass")
            go = st.form_submit_button("Log in")
        if go:
            uname = username.strip().lower()
            if uname in users and users[uname]["pw"] == hash_pw(uname, password):
                st.session_state.user = uname
                st.session_state.tour_step = None if users[uname]["toured"] else 0
                st.rerun()
            st.markdown('<div class="hf-note">Wrong username or password. New here? Use the Sign up tab.</div>', unsafe_allow_html=True)
    with tab_up:
        with st.form("signup_form"):
            name = st.text_input("Your name", key="su_name")
            username = st.text_input("Choose a username", key="su_user")
            password = st.text_input("Password (at least 4 characters)", type="password", key="su_pass")
            confirm = st.text_input("Confirm password", type="password", key="su_confirm")
            go = st.form_submit_button("Create account")
        if go:
            uname = username.strip().lower()
            problem = None
            if not name.strip():
                problem = "Please enter your name."
            elif not USERNAME_RE.fullmatch(uname):
                problem = "Usernames need 3-20 characters: letters, numbers, dots or underscores."
            elif len(password) < 4:
                problem = "Your password needs at least 4 characters."
            elif password != confirm:
                problem = "The two passwords don't match."
            elif uname in users:
                problem = "That username is taken. Try another one."
            if problem:
                st.markdown(f'<div class="hf-note">{esc(problem)}</div>', unsafe_allow_html=True)
            else:
                users[uname] = new_user(uname, name.strip(), password)
                st.session_state.user = uname
                st.session_state.tour_step = 0
                st.rerun()
    st.caption("Accounts and progress are kept in this browser session. Refreshing the page starts a fresh session.")


def render_sidebar(u):
    p = u["prefs"]
    with st.sidebar:
        pointer("sidebar")
        st.markdown(f'<div class="hf-side-brand">🌿 {esc(u["app_name"])}</div>'
                    f'<div class="hf-side-user">Signed in as {esc(u["name"])} (@{esc(st.session_state.user)})</div>', unsafe_allow_html=True)
        st.toggle("🌙 Dark mode", value=st.session_state.dark, key="dark_toggle",
                  on_change=set_theme, args=("dark_toggle",))

        st.markdown('<div class="hf-side-h">Profile</div>', unsafe_allow_html=True)
        with st.form("settings_form"):
            st.text_input("App name", value=u["app_name"], key="set_app")
            st.text_input("Your name", value=u["name"], key="set_name")
            st.form_submit_button("💾 Save settings", on_click=save_settings)

        st.markdown('<div class="hf-side-h">Account</div>', unsafe_allow_html=True)
        with st.expander("👤 Account & security"):
            st.markdown('<div class="hf-side-h">Change username</div>', unsafe_allow_html=True)
            with st.form("username_form", clear_on_submit=True):
                st.text_input("New username", key="acc_new_user")
                st.text_input("Current password", type="password", key="acc_user_pw")
                st.form_submit_button("Update username", on_click=change_username)
            st.markdown('<div class="hf-side-h">Change password</div>', unsafe_allow_html=True)
            with st.form("password_form", clear_on_submit=True):
                st.text_input("Current password", type="password", key="pw_cur")
                st.text_input("New password", type="password", key="pw_new")
                st.text_input("Confirm new password", type="password", key="pw_conf")
                st.form_submit_button("Update password", on_click=change_password)
            st.markdown('<div class="hf-side-h">Delete account</div>', unsafe_allow_html=True)
            st.text_input("Confirm with your password", type="password", key="acct_pw")
            sure_del = st.checkbox("Yes, delete my account and all its data", key="acct_confirm")
            st.button("Delete account", key="acct_delete", on_click=delete_account, disabled=not sure_del)

        st.markdown('<div class="hf-side-h">Reminders & effects</div>', unsafe_allow_html=True)
        st.toggle("🔔 Reminder notifications", value=p["notify"], key="pf_notify",
                  on_change=set_pref, args=("notify", "pf_notify"))
        st.toggle("🔊 Sound effects", value=p["sound"], key="pf_sound",
                  on_change=set_pref, args=("sound", "pf_sound"))
        st.toggle("🎊 Confetti & particles", value=p["fx"], key="pf_fx",
                  on_change=set_pref, args=("fx", "pf_fx"))
        st.number_input("Default reminder (minutes)", min_value=0, max_value=240, step=5,
                        value=int(p["default_remind"]), key="pf_remind",
                        on_change=set_pref, args=("default_remind", "pf_remind"))

        st.markdown('<div class="hf-side-h">Data</div>', unsafe_allow_html=True)
        with st.expander("🗂️ Data & reset"):
            st.button("Clear completed goals", key="rs_done", on_click=clear_done)
            st.button("Clear tip history", key="rs_tips", on_click=clear_tips)
            sure = st.checkbox("I understand this deletes my goals, tips and preferences", key="rs_confirm")
            st.button("Reset all my data (keep account)", key="rs_all", on_click=reset_all, disabled=not sure)

        st.button("🧭 Replay tour", key="replay", on_click=replay_tour)
        st.button("Log out", key="logout", on_click=logout)


def render_header(u):
    goals = u["goals"]
    today = date.today()
    active = [g for g in goals if not g["done"]]
    done_today = [g for g in goals if g["done"] and datetime.fromtimestamp(g["done_at"]).date() == today]
    done_total = [g for g in goals if g["done"]]
    now = datetime.now()
    st.markdown(
        f'<div class="hf-hero"><span class="hf-orb" style="width:130px;height:130px;right:-30px;top:-34px"></span>'
        f'<span class="hf-orb" style="width:70px;height:70px;right:130px;bottom:-24px;animation-delay:-2s"></span>'
        f'<div class="hf-date">{now:%A, %d %B}</div><div class="hf-title">{esc(u["app_name"])}</div>'
        f'<div class="hf-sub">{greeting()}, {esc(u["name"])}! Set a goal, check in with your mood and keep your streak glowing.</div></div>',
        unsafe_allow_html=True,
    )
    stats = [(len(active), "Active goals"), (len(done_today), "Done today"),
             (len(done_total), "Total completed"), (f"🔥 {streak_days(goals)}", "Day streak")]
    cells = "".join(f'<div class="hf-stat"><b>{v}</b><span>{label}</span></div>' for v, label in stats)
    st.markdown(f'<div class="hf-stats">{cells}</div>', unsafe_allow_html=True)


def render_tour(u):
    step = st.session_state.tour_step
    if step is None:
        return
    _, title, text = TOUR[step]
    if step == 0:
        text = f"Hi {u['name']}! " + text
    dots = "".join(f'<span class="{"on" if i <= step else ""}"></span>' for i in range(len(TOUR)))
    st.markdown(
        f'<div class="hf-tour"><div class="hf-step">Quest guide · step {step + 1} of {len(TOUR)}</div>'
        f'<div class="hf-ttl">🧭 {esc(title)}</div><div>{esc(text)}</div><div class="hf-dots">{dots}</div></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.button("◀ Back", key="tour_back", on_click=tour_move, args=(-1,), disabled=step == 0)
    c2.button("Finish 🎉" if step == len(TOUR) - 1 else "Next ▶", key="tour_next", on_click=tour_move, args=(1,))
    c3.button("Skip tour", key="tour_skip", on_click=tour_end, args=(False,))


def goal_row(g):
    with st.container(key=f"goal_{g['id']}"):
        c1, c2 = st.columns([8, 1])
        label = f"~~{g['title']}~~" if g["done"] else g["title"]
        c1.checkbox(label, value=g["done"], key=f"chk_{g['id']}", on_change=toggle_goal, args=(g["id"],))
        bits = [f'<span class="hf-badge">{GOAL_TYPES.get(g["type"], "🎯")} {esc(g["type"])}</span>',
                f'<span class="hf-meta">added {fmt_ts(g["created"])}</span>']
        if g["done"]:
            bits.append(f'<span class="hf-meta ok">✅ done {fmt_ts(g["done_at"])}</span>')
        elif g["due"]:
            bits.append(f'<span class="hf-meta">⏰ reminder at {datetime.fromtimestamp(g["due"]):%I:%M %p}</span>')
        c1.markdown(f'<div class="hf-metarow">{"".join(bits)}</div>', unsafe_allow_html=True)
        c2.button("🗑", key=f"del_{g['id']}", on_click=delete_goal, args=(g["id"],), help="Delete this goal")


def render_goals(u):
    today = date.today()
    active = [g for g in u["goals"] if not g["done"]]
    done_today = [g for g in u["goals"] if g["done"] and datetime.fromtimestamp(g["done_at"]).date() == today]
    total = len(active) + len(done_today)
    pct = int(100 * len(done_today) / total) if total else 0
    with st.container(key="sec_goals"):
        pointer("sec_goals")
        section_head("🎯 Today's goals", "Short-term pushes, long-term dreams and daily habits, all in one place.")
        with st.form("goal_form", clear_on_submit=True):
            st.text_input("What's your goal?", key="new_title", placeholder="e.g. Finish chapter 3 of physics")
            c1, c2 = st.columns(2)
            c1.selectbox("Goal type", list(GOAL_TYPES), key="new_type", format_func=lambda t: f"{GOAL_TYPES[t]}  {t}")
            c2.number_input("Remind me in (minutes, 0 = off)", min_value=0, max_value=1440, step=5,
                            value=int(u["prefs"]["default_remind"]), key="new_mins")
            st.form_submit_button("➕ Add goal", on_click=submit_goal)
        st.markdown(bar_html(pct, f"{len(done_today)} of {total} done today"), unsafe_allow_html=True)
        if not total:
            st.markdown('<div class="hf-empty">No goals yet. Add your first one above and make today count.</div>', unsafe_allow_html=True)
        for g in active + done_today:
            goal_row(g)


def reminders_panel():
    u = me()
    now = time.time()
    rows = [g for g in u["goals"] if g["due"] and not g["done"]]
    if not rows:
        st.markdown('<div class="hf-empty">No active reminders. Add a reminder time when you create a goal.</div>', unsafe_allow_html=True)
        return
    ring = False
    for g in rows:
        left = g["due"] - now
        late = left <= 0
        if late and not g["notified"]:
            g["notified"] = True
            ring = True
            if u["prefs"]["notify"]:
                st.toast(f"⏰ Time to work on: {g['title']}")
        span = max(g["due"] - g["start"], 1)
        pct = int(min(max((now - g["start"]) / span, 0), 1) * 100)
        status = "Time's up!" if late else fmt_clock(left)
        c1, c2 = st.columns([5, 1])
        c1.markdown(
            f'<div class="hf-rem{" late" if late else ""}"><div class="hf-rem-top"><span>⏰ {esc(g["title"])}</span>'
            f'<span class="hf-time">{status}</span></div><div class="hf-bar"><i style="width:{pct}%"></i></div></div>',
            unsafe_allow_html=True,
        )
        c2.button("+5 min", key=f"snz_{g['id']}", on_click=snooze, args=(g["id"],))
    if ring and u["prefs"]["sound"]:
        components.html(BEEP, height=0)


def render_reminders(u):
    ticking = any(g["due"] and not g["done"] for g in u["goals"])
    with st.container(key="sec_reminders"):
        pointer("sec_reminders")
        section_head("⏰ Reminders & timers", "Live countdowns for goals that have a reminder.")
        st.fragment(reminders_panel, run_every=1 if ticking else None)()


def render_mood(u):
    active = [g for g in u["goals"] if not g["done"]]
    titles = {g["id"]: g["title"] for g in active}
    options = [0] + list(titles)
    if st.session_state.get("focus_pick", 0) not in options:
        st.session_state.focus_pick = 0
    with st.container(key="sec_mood"):
        pointer("sec_mood")
        section_head("🧠 Mood check-in & AI tip", "Tell me how you feel and I'll tailor a tip to you and your goal.")
        c1, c2 = st.columns(2)
        c1.selectbox("How are you feeling?", list(MOODS), key="mood_pick", format_func=lambda m: f"{MOODS[m]}  {m}")
        c2.selectbox("Tip for which goal?", options, key="focus_pick",
                     format_func=lambda i: "✨ No specific goal" if i == 0 else titles[i])
        st.button("✨ Get AI Tip", key="tip_btn", on_click=give_tip)
        if u["tips"]:
            t = u["tips"][-1]
            foot = f"{fmt_ts(t['ts'])}" + (f" · for “{esc(t['goal'])}”" if t["goal"] else "")
            st.markdown(
                f'<div class="hf-tipcard"><span class="hf-tipmood">{MOODS[t["mood"]]} {t["mood"]}</span>'
                f'<div class="hf-tiptext">{esc(t["text"])}</div><div class="hf-tipfoot">{foot}</div></div>',
                unsafe_allow_html=True,
            )


def render_history(u):
    done = sorted((g for g in u["goals"] if g["done"]), key=lambda g: g["done_at"], reverse=True)
    total = len(u["goals"])
    pct = int(100 * len(done) / total) if total else 0
    with st.container(key="sec_history"):
        pointer("sec_history")
        section_head("📈 Progress & history", "Everything you complete and every tip you receive is saved here.")
        st.markdown(bar_html(pct, f"{len(done)} of {total} goals completed overall"), unsafe_allow_html=True)
        t1, t2 = st.tabs(["✅ Completed goals", "💡 Tip history"])
        with t1:
            if not done:
                st.markdown('<div class="hf-empty">Completed goals will appear here with a checkmark.</div>', unsafe_allow_html=True)
            for g in done[:25]:
                st.markdown(
                    f'<div class="hf-row"><span class="hf-check">✓</span><div><div class="hf-rt">{esc(g["title"])}</div>'
                    f'<div class="hf-rm">{GOAL_TYPES.get(g["type"], "🎯")} {esc(g["type"])} · added {fmt_ts(g["created"])} · done {fmt_ts(g["done_at"])}</div></div></div>',
                    unsafe_allow_html=True,
                )
        with t2:
            if not u["tips"]:
                st.markdown('<div class="hf-empty">Your generated tips will be saved here.</div>', unsafe_allow_html=True)
            for t in reversed(u["tips"][-15:]):
                goal = f" · for “{esc(t['goal'])}”" if t["goal"] else ""
                st.markdown(
                    f'<div class="hf-row"><span class="hf-check">{MOODS[t["mood"]]}</span><div><div class="hf-rt">{esc(t["text"])}</div>'
                    f'<div class="hf-rm">{esc(t["mood"])} · {fmt_ts(t["ts"])}{goal}</div></div></div>',
                    unsafe_allow_html=True,
                )


def render_effects(u):
    flash = st.session_state.pop("flash", None)
    if flash:
        st.toast(flash)
    if st.session_state.pop("fx_pending", False):
        if u["prefs"]["fx"]:
            st.session_state.fx_n += 1
            st.markdown(confetti_markup(st.session_state.fx_n), unsafe_allow_html=True)
        if u["prefs"]["sound"]:
            components.html(BEEP, height=0)
    step = st.session_state.tour_step
    if step is not None and st.session_state.get("scroll_step") != step:
        st.session_state.scroll_step = step
        target = TOUR[step][0]
        if target not in ("hero", "sidebar"):
            components.html(
                "<script>try{const el=window.parent.document.querySelector('.st-key-" + target +
                "');if(el){el.scrollIntoView({behavior:'smooth',block:'center'});}}catch(e){}</script>",
                height=0,
            )


def dashboard():
    u = me()
    if u["app_name"] in LEGACY_NAMES:
        u["app_name"] = APP_NAME
        st.session_state["set_app"] = APP_NAME
    render_sidebar(u)
    render_header(u)
    render_tour(u)
    render_goals(u)
    render_reminders(u)
    render_mood(u)
    render_history(u)
    render_effects(u)


# ------------------------------------------------------------------- main
for key, default in (("users", {}), ("user", None), ("dark", False), ("tour_step", None), ("fx_n", 0)):
    st.session_state.setdefault(key, default)

if st.session_state.user not in st.session_state.users:
    st.session_state.user = None

step_now = st.session_state.tour_step
tour_target = TOUR[step_now][0] if (st.session_state.user and step_now is not None) else None
st.markdown(build_css(st.session_state.dark, tour_target), unsafe_allow_html=True)

if st.session_state.user:
    dashboard()
else:
    auth_screen()