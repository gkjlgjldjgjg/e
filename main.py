from highrise import *
from highrise.models import *
from asyncio import run as arun
from flask import Flask
from threading import Thread
from highrise.__main__ import *
import random
import asyncio
import time
import json
import os
import shutil
from datetime import datetime
import logging
import logging.handlers

# إعداد نظام التسجيل (logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'bot_logs.log', maxBytes=10*1024*1024, backupCount=3, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.emote_looping = False
        self.user_emote_loops = {}
        self.loop_task = None
        self.is_teleporting_dict = {}
        self.following_user = None
        self.following_user_id = None
        self.kus = {}
        self.user_positions = {}
        self.position_tasks = {}
        self.dance_tasks = {}
        self.current_dances = {}
        self.last_emote_time = {}

        # قوائم المستخدمين والصلاحيات
        self.user_list = self.load_user_list()
        self.welcome_admins = ["7_e", "XQ5"]
        self.welcome_messages = self.load_welcome_messages()
        self.ban_log_file = "ban_logs.txt"

        # مواقع النقل المحددة
        self.teleport_locations = {
            "فوق": Position(13.0, 7.25, 10.0),
            "up": Position(13.0, 7.25, 10.0),
            "down": Position(12.5, 0.25, 17.0),  # الموقع الجديد
            "تحت": Position(12.5, 0.25, 17.0),
            "فوق2": Position(13.5, 15.25, 19.5),
            "vip": Position(6.0, 14.0, 7.0)
        }

        if not os.path.exists(self.ban_log_file):
            with open(self.ban_log_file, 'w', encoding='utf-8') as f:
                f.write("سجل عمليات الطرد:\n\n")

        # قائمة كاملة للرقصات والإيماءات (معدلة إلى tuples)
        self.dance_list = [
            (1, "Kawaii Go Go", "dance-kawai", 10.851059913635254, True),
            (2, "Hyped", "emote-hyped", 7.621847867965698, True),
            (3, "Levitate", "emoji-halo", 6.522106409072876, True),
            (4, "Hero Pose", "idle-hero", 22.32689070701599, True),
            (5, "Zero Gravity", "emote-astronaut", 13.933730125427246, True),
            (6, "Zombie Run", "emote-zombierun", 10.045882940292358, True),
            (7, "Dab", "emote-dab", 3.754014015197754, True),
            (8, "Do The Worm", "emote-snake", 6.629446268081665, True),
            (9, "Bummed", "idle-loop-sad", 21.796815395355225, True),
            (10, "Chillin'", "idle-loop-happy", 19.79949164390564, True),
            (11, "Sweet Smooch", "emote-kissing", 6.693175315856934, True),
            (12, "emoji-shush", "emoji-shush", 3.399787425994873, True),
            (13, "idle_tough", "idle_tough", 28.643417358398438, True),
            (14, "emote-fail3", "emote-fail3", 7.062429189682007, True),
            (15, "emote-shocked", "emote-shocked", 5.588654518127441, True),
            (16, "emote-theatrical-test", "emote-theatrical-test", 10.855672359466553, True),
            (17, "emote-fireworks", "emote-fireworks", 13.147647380828857, True),
            (18, "emote-receive-disappointed", "emote-receive-disappointed", 7.139604330062866, True),
            (19, "emote-confused2", "emote-confused2", 10.05685830116272, True),
            (20, "mining-mine", "mining-mine", 5.022986173629761, True),
            (21, "mining-success", "mining-success", 3.105142116546631, True),
            (22, "mining-fail", "mining-fail", 3.4111127853393555, True),
            (23, "Landing a Fish!", "fishing-pull", 2.8099365234375, True),
            (24, "Now We Wait...", "fishing-idle", 17.87005352973938, True),
            (25, "Casting!", "fishing-cast", 2.8209285736083984, True),
            (26, "We Have a Strike!", "fishing-pull-small", 3.6690878868103027, True),
            (27, "Hip Shake", "dance-hipshake", 13.383699655532837, True),
            (28, "Fruity Dance", "dance-fruity", 18.252850770950317, True),
            (29, "Cheer", "dance-cheerleader", 17.928509950637817, True),
            (30, "Magnetic", "dance-tiktok14", 11.197176218032837, True),
            (31, "Fairy Twirl", "emote-looping", 9.88614821434021, True),
            (32, "Fairy Float", "idle-floating", 27.596596002578735, True),
            (33, "Karma Dance", "dance-wild", 16.25053095817566, True),
            (34, "Moonlit Howl", "emote-howl", 8.101369619369507, True),
            (35, "Nocturnal Howl", "idle-howl", 48.618348360061646, True),
            (36, "Trampoline", "emote-trampoline", 6.105925559997559, True),
            (37, "Launch", "emote-launch", 10.881689548492432, True),
            (38, "Cute Salute", "emote-cutesalute", 3.7876434326171875, True),
            (39, "At Attention", "emote-salute", 4.789774417877197, True),
            (40, "Wop Dance", "dance-tiktok11", 11.368684530258179, True),
            (41, "Push It", "dance-employee", 8.551076650619507, True),
            (42, "This Is For You!", "emote-gift", 6.091700553894043, True),
            (43, "Sweet Little Moves", "dance-touch", 13.148397445678711, True),
            (44, "Repose", "sit-relaxed", 31.21304678916931, True),
            (45, "Sleigh Ride", "emote-sleigh", 12.514251470565796, True),
            (46, "Gimme Attention!", "emote-attention", 5.653335809707642, True),
            (47, "Jingle Hop", "dance-jinglebell", 12.085973262786865, True),
            (48, "Timejump", "emote-timejump", 5.513711452484131, True),
            (49, "Gotta Go!", "idle-toilet", 33.481799602508545, True),
            (50, "Bit Nervous", "idle-nervous", 22.80543065071106, True),
            (51, "Scritchy", "idle-wild", 27.349984645843506, True),
            (52, "Ice Skating", "emote-iceskating", 8.409219026565552, True),
            (53, "Laid Back", "sit-open", 27.275065183639526, True),
            (54, "Party Time!", "emote-celebrate", 4.345993518829346, True),
            (55, "Shrink", "emote-shrink", 9.985114097595215, True),
            (56, "Arabesque", "emote-pose10", 5.0028111934661865, True),
            (57, "Bashful Blush", "emote-shy2", 6.3357625007629395, True),
            (58, "Possessed Puppet", "emote-puppet", 17.886415243148804, True),
            (59, "Revelations", "emote-headblowup", 13.659945964813232, True),
            (60, "Watch Your Back", "emote-creepycute", 9.010944843292236, True),
            (61, "Creepy Puppet", "dance-creepypuppet", 7.789044618606567, True),
            (62, "Saunter Sway", "dance-anime", 9.595806360244751, True),
            (63, "Groovy Penguin", "dance-pinguin", 12.809289932250977, True),
            (64, "Air Guitar", "idle-guitar", 14.151675462722778, True),
            (65, "Ready To Rumble", "emote-boxer", 6.754365921020508, True),
            (66, "Celebration Step", "emote-celebrationstep", 5.181864023208618, True),
            (67, "Big Surprise", "emote-pose6", 6.458929777145386, True),
            (68, "Ditzy pose", "emote-pose9", 6.004010438919067, True),
            (69, "Stargazing", "emote-stargazer", 7.928274631500244, True),
            (70, "dance-wrong", "dance-wrong", 13.59788990020752, True),
            (71, "UWU Mood", "idle-uwu", 25.496710538864136, True),
            (72, "emote-fashionista", "emote-fashionista", 6.325819730758667, True),
            (73, "dance-icecream", "dance-icecream", 16.57703709602356, True),
            (74, "emote-gravity", "emote-gravity", 9.024450540542603, True),
            (75, "emote-punkguitar", "emote-punkguitar", 10.592331171035767, True),
            (76, "Say So Dance", "idle-dance-tiktok4", 16.550219535827637, True),
            (77, "I'm A Cutie!", "emote-cutey", 4.068171739578247, True),
            (78, "Fashion Pose", "emote-pose5", 5.489050388336182, True),
            (79, "I Challenge You!", "emote-pose3", 5.565914154052734, True),
            (80, "Flirty Wink", "emote-pose1", 4.714804410934448, True),
            (81, "A Casual Dance", "idle-dance-casual", 9.570026159286499, True),
            (82, "Cheerful", "emote-pose8", 5.618878126144409, True),
            (83, "Embracing Model", "emote-pose7", 5.2841644287109375, True),
            (84, "Fighter", "idle-fighter", 18.63888120651245, True),
            (85, "Shuffle Dance", "dance-tiktok10", 9.410870790481567, True),
            (86, "Renegade", "idle-dance-tiktok7", 14.047954082489014, True),
            (87, "Grave Dance", "dance-weird", 22.866037607192993, True),
            (88, "Viral Groove", "dance-tiktok9", 13.03692102432251, True),
            (89, "emote-cute", "emote-cute", 7.200940847396851, True),
            (90, "Lambi's Pose", "emote-superpose", 5.434790134429932, True),
            (91, "Froggie Hop", "emote-frog", 16.1352436542511, True),
            (92, "Sing Along", "idle_singing", 11.307929277420044, True),
            (93, "Energy Ball", "emote-energyball", 8.284976243972778, True),
            (94, "Maniac", "emote-maniac", 5.944519519805908, True),
            (95, "Sword Fight", "emote-swordfight", 7.7122719287872314, True),
            (96, "Teleport", "emote-teleporting", 12.893966674804688, True),
            (97, "Floating", "emote-float", 9.257302045822144, True),
            (98, "Telekinesis", "emote-telekinesis", 11.01258134841919, True),
            (99, "Slap", "emote-slap", 4.059824228286743, True),
            (100, "Pissed Off", "emote-frustrated", 6.4050421714782715, True),
            (101, "Embarrassed", "emote-embarrassed", 9.089924573898315, True),
            (102, "Enthused", "idle-enthusiastic", 17.52780532836914, True),
            (103, "Confusion", "emote-confused", 9.584890842437744, True),
            (104, "Let's Go Shopping", "dance-shoppingcart", 5.558927774429321, True),
            (105, "ROFL!", "emote-rofl", 7.650259494781494, True),
            (106, "Roll", "emote-roll", 4.306966066360474, True),
            (107, "Super Run", "emote-superrun", 7.162847995758057, True),
            (108, "Super Punch", "emote-superpunch", 5.751260757446289, True),
            (109, "Super Kick", "emote-kicking", 6.213217496871948, True),
            (110, "Falling Apart", "emote-apart", 5.977605819702148, True),
            (111, "Partner Hug", "emote-hug", 4.525649547576904, True),
            (112, "Secret Handshake", "emote-secrethandshake", 6.280278205871582, True),
            (113, "Peekaboo!", "emote-peekaboo", 4.521607160568237, True),
            (114, "Monster Fail", "emote-monster_fail", 5.419337272644043, True),
            (115, "Zombie Dance", "dance-zombie", 13.830149173736572, True),
            (116, "Rope Pull", "emote-ropepull", 10.6853609085083, True),
            (117, "Proposing", "emote-proposing", 5.909177303314209, True),
            (118, "Sumo Fight", "emote-sumo", 11.644229650497437, True),
            (119, "Charging", "emote-charging", 9.532383680343628, True),
            (120, "Ninja Run", "emote-ninjarun", 6.499711513519287, True),
            (121, "Elbow Bump", "emote-elbowbump", 6.438911199569702, True),
            (122, "Irritated", "idle-angry", 26.070024013519287, True),
            (123, "Home Run!", "emote-baseball", 8.472715139389038, True),
            (124, "Cozy Nap", "idle-floorsleeping", 14.611307382583618, True),
            (125, "Relaxing", "idle-floorsleeping2", 18.827470779418945, True),
            (126, "Hug Yourself", "emote-hugyourself", 6.028209686279297, True),
            (127, "Pouty Face", "idle-sad", 25.23569631576538, True),
            (128, "Collapse", "emote-death2", 5.543778896331787, True),
            (129, "Level Up!", "emote-levelup", 7.271570920944214, True),
            (130, "Posh", "idle-posh", 23.29422426223755, True),
            (131, "Snow Angel", "emote-snowangel", 7.334203720092773, True),
            (132, "Sweating", "emote-hot", 5.572302341461182, True),
            (133, "Snowball Fight!", "emote-snowball", 6.320742130279541, True),
            (134, "Ponder", "idle-lookup", 8.754379272460938, True),
            (135, "Curtsy", "emote-curtsy", 3.9908952713012695, True),
            (136, "Russian Dance", "dance-russian", 11.388729810714722, True),
            (137, "Bow", "emote-bow", 5.102638483047485, True),
            (138, "Boo", "emote-boo", 5.578845024108887, True),
            (139, "Fall", "emote-fail1", 6.896064758300781, True),
            (140, "Clumsy", "emote-fail2", 7.742251634597778, True),
            (141, "Imaginary Jetpack", "emote-jetpack", 17.774274826049805, True),
            (142, "Revival", "emote-death", 8.003193378448486, True),
            (143, "Penny's Dance", "dance-pennywise", 4.157809495925903, True),
            (144, "Sleepy", "idle-sleep", 3.353527307510376, True),
            (145, "Attentive", "idle_layingdown", 26.108940839767456, True),
            (146, "Theatrical", "emote-theatrical", 10.995978116989136, True),
            (147, "Faint", "emote-fainting", 18.552194118499756, True),
            (148, "Relaxed", "idle_layingdown2", 22.587023496627808, True),
            (149, "I Believe I Can Fly", "emote-wings", 14.205503702163696, True),
            (150, "Amused", "emote-laughing2", 6.60427188873291, True),
            (151, "Don't Start Now", "dance-tiktok2", 11.37182092666626, True),
            (152, "Model", "emote-model", 7.427884817123413, True),
            (153, "K-Pop Dance", "dance-blackpink", 7.974578857421875, True),
            (154, "Sick", "emoji-sick", 6.217142343521118, True),
            (155, "Zombie", "idle_zombie", 31.391045093536377, True),
            (156, "Cold", "emote-cold", 5.168632745742798, True),
            (157, "Bunny Hop", "emote-bunnyhop", 13.63294768333435, True),
            (158, "Disco", "emote-disco", 6.136807441711426, True),
            (159, "Wiggle Dance", "dance-sexy", 13.704560279846191, True),
            (160, "Heart Hands", "emote-heartfingers", 5.182276487350464, True),
            (161, "Savage Dance", "dance-tiktok8", 13.10374116897583, True),
            (162, "Ghost Float", "emote-ghost-idle", 20.427579641342163, True),
            (163, "Sneeze", "emoji-sneeze", 4.327379941940308, True),
            (164, "Pray", "emoji-pray", 6.003554344177246, True),
            (165, "Handstand", "emote-handstand", 5.886280059814453, True),
            (166, "Smoothwalk", "dance-smoothwalk", 7.581580400466919, True),
            (167, "Ring on It", "dance-singleladies", 22.333438873291016, True),
            (168, "Partner Heart Arms", "emote-heartshape", 7.5974767208099365, True),
            (169, "Ghost", "emoji-ghost", 3.7432401180267334, True),
            (170, "Push Ups", "dance-aerobics", 9.887983083724976, True),
            (171, "Naughty", "emoji-naughty", 5.731683254241943, True),
            (172, "Faint Drop", "emote-deathdrop", 4.177362442016602, True),
            (173, "Duck Walk", "dance-duckwalk", 12.48209023475647, True),
            (174, "Splits Drop", "emote-splitsdrop", 5.310996055603027, True),
            (175, "Vogue Hands", "dance-voguehands", 10.565007209777832, True),
            (176, "Give Up", "emoji-give-up", 6.040206670761108, True),
            (177, "Smirk", "emoji-smirking", 5.7423319816589355, True),
            (178, "Lying", "emoji-lying", 7.389834403991699, True),
            (179, "Arrogance", "emoji-arrogance", 8.159849882125854, True),
            (180, "Point", "emoji-there", 3.0896713733673096, True),
            (181, "Stinky", "emoji-poop", 5.85624885559082, True),
            (182, "Fireball Lunge", "emoji-hadoken", 4.290197372436523, True),
            (183, "Punch", "emoji-punch", 3.361440658569336, True),
            (184, "Hands in the Air", "dance-handsup", 23.177976608276367, True),
            (185, "Rock Out", "dance-metal", 15.781339168548584, True),
            (186, "Orange Juice Dance", "dance-orangejustice", 7.168856620788574, True),
            (187, "Aerobics", "idle-loop-aerobics", 10.082928657531738, True),
            (188, "Annoyed", "idle-loop-annoyed", 18.624611854553223, True),
            (189, "Gasp", "emoji-scared", 4.064062595367432, True),
            (190, "Think", "emote-think", 4.805848598480225, True),
            (191, "Fatigued", "idle-loop-tired", 11.23218560218811, True),
            (192, "Feel The Beat", "idle-dance-headbobbing", 23.653693914413452, True),
            (193, "Blast Off", "emote-disappear", 5.531318426132202, True),
            (194, "Sob", "emoji-crying", 4.9091150760650635, True),
            (195, "Tap Loop", "idle-loop-tapdance", 7.8087074756622314, True),
            (196, "Raise The Roof", "emoji-celebrate", 4.7828662395477295, True),
            (197, "Eye Roll", "emoji-eyeroll", 3.7542595863342285, True),
            (198, "Stunned", "emoji-dizzy", 5.3762526512146, True),
            (199, "Tummy Ache", "emoji-gagging", 6.836994409561157, True),
            (200, "Greedy Emote", "emote-greedy", 5.720172643661499, True),
            (201, "Mind Blown", "emoji-mind-blown", 3.4589083194732666, True),
            (202, "Shy", "emote-shy", 5.146667718887329, True),
            (203, "Clap", "emoji-clapping", 2.9828615188598633, True),
            (204, "Love Flutter", "emote-hearteyes", 5.989662170410156, True),
            (205, "Thumb Suck", "emote-suckthumb", 5.227030992507935, True),
            (206, "Exasperated", "emote-exasperated", 4.09885573387146, True),
            (207, "Jump", "emote-jumpb", 4.87456488609314, True),
            (208, "Face Palm", "emote-exasperatedb", 3.8919904232025146, True),
            (209, "Peace", "emote-peace", 7.00889253616333, True),
            (210, "The Wave", "emote-wave", 4.0621178150177, True),
            (211, "Panic", "emote-panic", 3.7224788665771484, True),
            (212, "Harlem Shake", "emote-harlemshake", 14.377963066101074, True),
            (213, "Tap Dance", "emote-tapdance", 12.435080289840698, True),
            (214, "Gangnam Style", "emote-gangnam", 8.071059703826904, True),
            (215, "No", "emote-no", 3.8635921478271484, True),
            (216, "Sad", "emote-sad", 6.419863224029541, True),
            (217, "Yes", "emote-yes", 4.118977308273315, True),
            (218, "Kiss", "emote-kiss", 3.7398743629455566, True),
            (219, "Moonwalk", "emote-gordonshuffle", 9.52907681465149, True),
            (220, "Night Fever", "emote-nightfever", 6.344593524932861, True),
            (221, "Laugh", "emote-laughing", 3.7673463821411133, True),
            (222, "Judo Chop", "emote-judochop", 3.610184669494629, True),
            (223, "Rainbow", "emote-rainbow", 3.074357271194458, True),
            (224, "Robot", "emote-robot", 9.224223613739014, True),
            (225, "Happy", "emote-happy", 4.755821943283081, True),
            (226, "Angry", "emoji-angry", 6.322439670562744, True),
            (227, "Macarena", "dance-macarena", 13.161751747131348, True),
            (228, "Sit", "idle-loop-sitfloor", 23.04495859146118, True),
            (229, "Thumbs Up", "emoji-thumbsup", 3.779395580291748, True),
            (230, "Tired", "emote-tired", 5.9777562618255615, True),
            (231, "Hello", "emote-hello", 3.7342917919158936, True),
            (232, "ris", "sit-idle-cute", 17.733200788497925, False),
            (233, "Uhmmm", "emote-thought", 27.43184781074524, False),
            (234, "Crouch", "idle-crouched", 28.274845600128174, False),
            (235, "Wait", "dance-wait", 9.92491340637207, False),
            (236, "Ignition Boost", "hcc-jetpack", 27.44775152206421, False),
            (237, "run-vertical", "run-vertical", 3.8643360137939453, False),
            (238, "walk-vertical", "walk-vertical", 4.1798996925354, False),
            (239, "idle-phone", "idle-phone", 31.364736795425415, False),
            (240, "Blowing Kisses", "emote-blowkisses", 5.9789252281188965, False),
            (241, "Headball", "emote-headball", 11.664129972457886, False),
            (242, "Hero Entrance", "emote-hero", 6.587759494781494, False),
            (243, "Floss", "dance-floss", 23.12726402282715, False),
            (244, "Karate", "dance-martial-artist", 13.972932577133179, False),
            (245, "Robotic", "dance-robotic", 12.225102424621582, False),
            (246, "Graceful", "emote-graceful", 5.270719289779663, False),
            (247, "Frolic", "emote-frollicking", 5.087254524230957, False),
            (248, "Flex", "emoji-flex", 3.3146491050720215, False),
            (249, "Cursing Emote", "emoji-cursing", 3.8144092559814453, False),
            (250, "Flirty Wave", "emote-lust", 5.467925310134888, False),
            (251, "emote-", "emote-", 2.981541633605957, False),
            (252, "emote-holding-hot-cocoa", "emote-holding-hot-cocoa", 3.8734710216522217, False),
            (253, "emote-mittens", "emote-mittens", 3.169820785522461, False),
            (254, "Boogie Swing", "idle-dance-swinging", 14.46821665763855, False),
            (255, "Breakdance", "dance-breakdance", 17.939950466156006, False),
            (256, "ريست", "sit-open", 27.275065183639526, True),
            (257, "جوست", "emote-ghost-idle", 20.427579641342163, True),
            (258, "Yoga Flow", "dance-spiritual", 17.70866560935974, False)

        ]

    def load_user_list(self):
        """تحميل قائمة المستخدمين من ملف JSON"""
        try:
            if os.path.exists('user_list.json'):
                with open('user_list.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logging.info(f"تم تحميل {len(data)} مستخدم من القائمة")
                    return data
            return ["", "Abo_Hadram", "SU.E7"]
        except Exception as e:
            logging.error(f"Error loading user list: {e}")
            return ["", "Abo_Hadram", "SU.E7"]

    def save_user_list(self):
        """حفظ قائمة المستخدمين إلى ملف JSON"""
        try:
            with open('user_list.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_list, f, ensure_ascii=False, indent=4)
            logging.info(f"تم حفظ {len(self.user_list)} مستخدم في القائمة")
        except Exception as e:
            logging.error(f"Error saving user list: {e}")
    async def handle_text_dance_command(self, user: User, message: str) -> None:
        """معالجة أوامر الرقص بالنص"""
        dance_name = message.lower()
        for dance in self.dance_list:
            if dance[1].lower() == dance_name:  # العنصر الثاني هو name
                await self.start_continuous_dance(user, dance[2])  # العنصر الثالث هو emote_id
                return
        await self.highrise.chat("الرقصة غير موجودة في القائمة")
    async def handle_numeric_dance_command(self, user: User, message: str) -> None:
        """معالجة أوامر الرقص بالأرقام"""
        try:
            dance_num = int(message)
            if 1 <= dance_num <= len(self.dance_list):
                dance = self.dance_list[dance_num - 1]
                await self.start_continuous_dance(user, dance[2])  # العنصر الثالث هو emote_id
            else:
                await self.highrise.chat(f"رقم الرقصة يجب أن يكون بين 1 و{len(self.dance_list)}")
        except ValueError:
            await self.highrise.chat("الرجاء إدخال رقم صحيح")
    def load_welcome_messages(self):
        """تحميل رسائل الترحيب من ملف JSON"""
        try:
            if os.path.exists('welcome_messages.json'):
                with open('welcome_messages.json', 'r', encoding='utf-8') as f:
                    return {k.lower(): v for k, v in json.load(f).items()}
            return {}
        except Exception as e:
            logging.error(f"Error loading welcome messages: {e}")
            return {}

    def save_welcome_messages(self):
        """حفظ رسائل الترحيب إلى ملف JSON"""
        try:
            with open('welcome_messages.json', 'w', encoding='utf-8') as f:
                json.dump(self.welcome_messages, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Error saving welcome messages: {e}")

    def log_ban_action(self, moderator: str, banned_user: str):
        """تسجيل عملية الطرد في الملف"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{current_time}] المشرف @{moderator} قام بطرد @{banned_user}\n"
            with open(self.ban_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logging.error(f"حدث خطأ أثناء تسجيل عملية الطرد: {e}")

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        """عند بدء تشغيل البوت"""
        logging.info("Bot started successfully")
        try:
            await self.highrise.tg.create_task(self.highrise.teleport(
                session_metadata.user_id, Position(17.5, 0.25, 12.0, "FrontLeft")))
        except Exception as e:
            logging.error(f"Error in on_start: {e}")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        """عند دخول مستخدم إلى الغرفة"""
        try:
            self.welcome_messages = self.load_welcome_messages()
            welcome_message = None

            for username, msg in self.welcome_messages.items():
                if username.lower() == user.username.lower():
                    welcome_message = msg
                    break

            if welcome_message:
                await self.highrise.chat(welcome_message)
            else:
                 await self.highrise.chat(f" @{user.username} ,   ❤️ حيو من جانا نورت Bar 🍻🍺  يمز🔥 ❤️  ")



            try:
                dance = random.choice(self.dance_list)
                await self.send_emote_safe(dance[2], user.id)
            except Exception as e:
                logging.error(f"Error sending welcome emote to {user.username}: {e}")

        except Exception as e:
            logging.error(f"Error in on_user_join for {user.username}: {e}")
            await self.highrise.chat(f"مرحباً @{user.username} في الغرفة!")

    async def on_user_leave(self, user: User):
        """عند مغادرة مستخدم للغرفة"""
        user_id = user.id
        farewell_message = f" @{user.username} , 😢 يا حرام ياريت يرجع 😢"

        if user_id in self.dance_tasks:
            self.dance_tasks[user_id].cancel()
            del self.dance_tasks[user_id]

        if user_id in self.user_emote_loops:
            await self.stop_emote_loop(user_id)

        if user_id in self.current_dances:
            del self.current_dances[user_id]

        await self.highrise.chat(farewell_message)

    async def send_emote_safe(self, emote_id: str, user_id: str):
        """إرسال رقصة مع معالجة الأخطاء"""
        try:
            if not any(emote_id == dance[2] for dance in self.dance_list):
                logging.warning(f"Emote {emote_id} not found in dance list")
                return False

            await self.highrise.send_emote(emote_id, user_id)
            return True
        except Exception as e:

            return False

    async def handle_teleport_command(self, user: User, message: str) -> None:
        """معالجة أوامر النقل"""
        try:
            parts = message.split()
            command = parts[0].lower()

            if len(parts) > 1 and parts[1].startswith("@"):
                if user.username.lower() not in [u.lower() for u in self.user_list + self.welcome_admins]:
                    await self.highrise.chat(f"@{user.username} ليس لديك صلاحية نقل الآخرين!")
                    return

                target_username = parts[1][1:].lower()
                room_users = await self.highrise.get_room_users()
                target_user = None

                for u, pos in room_users.content:
                    if u.username.lower() == target_username:
                        target_user = u
                        break

                if not target_user:
                    await self.highrise.chat(f"المستخدم @{target_username} غير موجود في الغرفة!")
                    return

                if command in self.teleport_locations:
                    await self.highrise.teleport(target_user.id, self.teleport_locations[command])

            else:
                if command in ["فوق", "تحت", "down","up","فوق2"]:
                    if command in self.teleport_locations:
                        await self.highrise.teleport(user.id, self.teleport_locations[command])

                elif command == "vip":
                    if user.username.lower() in [u.lower() for u in self.user_list + self.welcome_admins]:
                        await self.highrise.teleport(user.id, self.teleport_locations["vip"])

        except Exception as e:
            logging.error(f"حدث خطأ أثناء معالجة أمر النقل: {e}")
            await self.highrise.chat("حدث خطأ أثناء معالجة الأمر!")

    async def start_continuous_dance(self, user: User, emote_id: str):
        """بدء رقصة مستمرة"""
        user_id = user.id

        if not any(emote_id == dance[2] for dance in self.dance_list):
            await self.highrise.send_whisper(user.id, f"الرقصة غير متوفرة حالياً")
            return

        if user_id in self.dance_tasks:
            self.dance_tasks[user_id].cancel()
            await asyncio.sleep(0.1)

        self.current_dances[user_id] = emote_id
        self.dance_tasks[user_id] = asyncio.create_task(
            self.dance_loop(user_id, emote_id))

    async def dance_loop(self, user_id: str, emote_id: str):
        """حلقة رقص معدلة توازن بين السلاسة والاستمرارية"""
        try:
            last_emote_time = 0

            while True:
                if user_id not in self.current_dances or self.current_dances[user_id] != emote_id:
                    break

                current_time = time.time()
                elapsed = current_time - last_emote_time
                emote_cooldown = self.get_dance_duration(emote_id) * 0.8  # 70% من مدة الرقصة

                if elapsed >= emote_cooldown:
                    try:
                        await self.send_emote_safe(emote_id, user_id)
                        last_emote_time = current_time
                    except Exception as e:
                        if "Target user not in room" in str(e):
                            break
                        logging.error(f"Error sending dance emote: {e}")
                        await asyncio.sleep(1)
                else:
                    # انتظار قصير جداً فقط لمنع الحمل الزائد
                    await asyncio.sleep(0.05)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Unexpected error in dance loop: {e}")
        finally:
            self.cleanup_dance_tasks(user_id)

    def get_dance_duration(self, emote_id: str) -> float:
        """الحصول على مدة الرقصة من القائمة"""
        for dance in self.dance_list:
            if dance[2] == emote_id:
                return dance[3]
        return 5.0

    def cleanup_dance_tasks(self, user_id: str):
        """تنظيف مهام الرقص"""
        if user_id in self.dance_tasks:
            try:
                self.dance_tasks[user_id].cancel()
            except:
                pass
            del self.dance_tasks[user_id]
        if user_id in self.current_dances:
            del self.current_dances[user_id]

    async def handle_emote_command(self, user_id: str, emote_name: str) -> None:
        """معالجة أوامر الإيماءات"""
        emote_name = emote_name.lower()
        dance = next((d for d in self.dance_list if d[1].lower() == emote_name), None)
        if dance:
            try:
                await self.send_emote_safe(dance[2], user_id)
            except Exception as e:
                logging.error(f"Error sending emote: {e}")

    async def start_emote_loop(self, user_id: str, emote_name: str) -> None:
        """بدء حلقة إيماءة"""
        dance = next((d for d in self.dance_list if d[1].lower() == emote_name.lower()), None)
        if dance:
            self.user_emote_loops[user_id] = emote_name
            while self.user_emote_loops.get(user_id) == emote_name:
                try:
                    await self.send_emote_safe(dance[2], user_id)
                except Exception as e:
                    if "Target user not in room" in str(e):
                        logging.info(f"{user_id} not in room, stopping emote loop.")
                        break
                await asyncio.sleep(5)

    async def stop_emote_loop(self, user_id: str) -> None:
        """إيقاف حلقة الإيماءة"""
        if user_id in self.user_emote_loops:
            self.user_emote_loops.pop(user_id)

    async def emote_loop(self):
        """حلقة الإيماءات العامة"""
        while True:
            try:
                dance = random.choice(self.dance_list)
                await self.send_emote_safe(emote_id=dance[2])
                await asyncio.sleep(5)
            except Exception as e:
                logging.error("Error sending emote:", e)

    async def start_random_emote_loop(self, user_id: str) -> None:
        """بدء حلقة إيماءات عشوائية"""
        self.user_emote_loops[user_id] = "dans"
        while self.user_emote_loops.get(user_id) == "dans":
            try:
                dance = random.choice(self.dance_list)
                await self.send_emote_safe(dance[2], user_id)
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(f"Error sending random emote: {e}")

    async def stop_random_emote_loop(self, user_id: str) -> None:
        """إيقاف حلقة الإيماءات العشوائية"""
        if user_id in self.user_emote_loops:
            del self.user_emote_loops[user_id]

    async def send_group_dance(self, user: User, message: str) -> None:
        """إرسال رقصة مستمرة لمجموعة من المستخدمين"""
        try:
            if user.username.lower() not in [u.lower() for u in self.user_list + self.welcome_admins]:
                await self.highrise.chat(f"@{user.username} هذا الأمر متاح فقط لأعضاء VIP والمشرفين!")
                return

            parts = message.split()
            if len(parts) < 1:
                await self.highrise.chat("استخدم: رقم_الرقصة @المستخدم1 @المستخدم2 ...")
                return

            dance_num = parts[0]
            if not dance_num.isdigit():
                await self.highrise.chat("الرجاء إدخال رقم الرقصة أولاً")
                return

            dance_num = int(dance_num)
            if dance_num < 1 or dance_num > len(self.dance_list):
                await self.highrise.chat(f"رقم الرقصة يجب أن يكون بين 1 و{len(self.dance_list)}")
                return

            dance = self.dance_list[dance_num-1]
            emote_id = dance[2]
            emote_name = dance[1]
            emote_duration = dance[3]

            usernames = [user.username.lower()]
            if len(parts) > 1:
                usernames += [part[1:].lower() for part in parts[1:] if part.startswith("@")]

            usernames = list(dict.fromkeys(usernames))
            room_users = await self.highrise.get_room_users()
            users_in_room = {u.username.lower(): u for u, _ in room_users.content}

            successful_users = []
            failed_users = []

            for username in usernames:
                target_user = users_in_room.get(username.lower())
                if target_user:
                    try:
                        await self.start_continuous_dance(target_user, emote_id)
                        successful_users.append(f"@{target_user.username}")
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logging.error(f"Failed to start dance for @{username}: {e}")
                        failed_users.append(f"@{username}")
                else:
                    failed_users.append(f"@{username}")

            result_message = f"تم تشغيل رقصة '{emote_name}' ({emote_duration:.1f} ثانية) بشكل مستمر: "

            if successful_users:
                if len(successful_users) > 5:
                    user_list = " , ".join(successful_users[:5])
                    remaining = len(successful_users) - 5
                    result_message += f"لـ {user_list} و{remaining} آخرين"
                else:
                    user_list = " , ".join(successful_users)
                    result_message += f"لـ {user_list}"

            if failed_users:
                result_message += f" | فشل الإرسال لـ: {', '.join(failed_users[:3])}"
                if len(failed_users) > 3:
                    result_message += f" و{len(failed_users)-3} آخرين"

            await self.highrise.chat(result_message)

        except Exception as e:
            logging.error(f"Error in send_group_dance: {e}")
            await self.highrise.chat("حدث خطأ أثناء محاولة إرسال الرقصة الجماعية")

    async def on_user_move(self, user: User, pos: Position) -> None:
        self.user_positions[user.username] = pos

    async def on_chat(self, user: User, message: str) -> None:
        """عند استقبال رسالة في الدردشة"""
        try:
            message = message.strip()

            if message and message[0].isdigit() and "@" in message:
                await self.send_group_dance(user, message)
                return

            if message.lower().startswith(("فوق", "تحت", "vip", "down","up","فوق2")):
                await self.handle_teleport_command(user, message.lower())
                return

            if message.lower() == "مكاني":
                if user.username in self.user_positions:
                    position = self.user_positions[user.username]
                    if isinstance(position, Position):
                        await self.highrise.chat(f"إحداثياتك الحالية يا {user.username} هي: x={position.x}, y={position.y}, z={position.z}")
                    elif isinstance(position, AnchorPosition):
                        await self.highrise.chat(f"{user.username} يجلس على كرسي في مكان غير محدد y.")
                    else:
                        await self.highrise.chat("لا أستطيع العثور على إحداثياتك الحالية.")
                else:
                    await self.highrise.chat("لا أستطيع العثور على إحداثياتك الحالية.")
                return

            if message.lower() in ["توقف", "stop", "0"]:
                if user.id in self.dance_tasks:
                    self.dance_tasks[user.id].cancel()
                    del self.dance_tasks[user.id]
                return

            if message.isdigit():
                await self.handle_numeric_dance_command(user, message)
                return

            if any(dance[1].lower() == message.lower() for dance in self.dance_list):
                await self.handle_text_dance_command(user, message)
                return
            if message.lower().startswith("!add @") and user.username in self.welcome_admins:
                try:
                    parts = message.split("@", 1)
                    if len(parts) < 2:
                        return

                    username_part, welcome_part = parts[1].split(maxsplit=1)
                    target_username = username_part.strip()
                    welcome_message = welcome_part.strip()

                    self.welcome_messages[target_username.lower()] = f"@{target_username} {welcome_message}"
                    self.save_welcome_messages()
                    await self.highrise.chat(f"تم إضافة ترحيب لـ @{target_username} بنجاح!")
                except Exception as e:
                    logging.error(f"Error adding welcome message: {e}")
                    await self.highrise.chat("حدث خطأ! استخدم الصيغة: !add @username رسالة الترحيب")

            elif message.lower().startswith("!remove @") and user.username in self.welcome_admins:
                try:
                    target_username = message.split("@")[1].strip().lower()
                    if target_username in self.welcome_messages:
                        del self.welcome_messages[target_username]
                        self.save_welcome_messages()
                        await self.highrise.chat(f"تم حذف ترحيب @{target_username} بنجاح")
                    else:
                        await self.highrise.chat(f"لا يوجد ترحيب مخصص لـ @{target_username}")
                except Exception as e:
                    logging.error(f"Error removing welcome message: {e}")
                    await self.highrise.chat("حدث خطأ! استخدم الصيغة: !remove @username")

            elif message.lower() == "!list welcomes" and user.username in self.welcome_admins:
                if not self.welcome_messages:
                    await self.highrise.chat("لا توجد ترحيبات مخصصة حالياً")
                else:
                    await self.highrise.chat("قائمة الترحيبات المخصصة:")
                    for username, welcome_msg in self.welcome_messages.items():
                        await self.highrise.chat(f"@{username}: {welcome_msg}")

            elif message.lower() == "!check welcomes" and user.username in self.welcome_admins:
                welcome_count = len(self.welcome_messages)
                await self.highrise.chat(f"نظام الترحيب يعمل بشكل صحيح. عدد الترحيبات المخصصة: {welcome_count}")
                await self.highrise.chat(f"آخر تحديث لرسائل الترحيب: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            if user.username in self.welcome_admins:
                if message.lower().startswith("اضف @"):
                    target_username = message.split("@")[1].strip()
                    self.user_list = self.load_user_list()

                    if target_username not in self.user_list:
                        self.user_list.append(target_username)
                        self.save_user_list()
                        self.user_list = self.load_user_list()
                        await self.highrise.chat(f"تم إضافة @{target_username} إلى قائمة VIP بنجاح")
                        logging.info(f"تمت إضافة @{target_username} إلى قائمة VIP بواسطة @{user.username}")
                    else:
                        await self.highrise.chat(f"@{target_username} موجود بالفعل في قائمة VIP")

                elif message.lower().startswith("حذف @"):
                    target_username = message.split("@")[1].strip()
                    self.user_list = self.load_user_list()

                    if target_username in self.user_list:
                        self.user_list.remove(target_username)
                        self.save_user_list()
                        self.user_list = self.load_user_list()
                        await self.highrise.chat(f"تم حذف @{target_username} من قائمة VIP بنجاح")
                        logging.info(f"تم حذف @{target_username} من قائمة VIP بواسطة @{user.username}")
                    else:
                        await self.highrise.chat(f"@{target_username} غير موجود في قائمة VIP")

                elif message.lower() == "عرض القائمة":
                    self.user_list = self.load_user_list()
                    if self.user_list:
                        await self.highrise.chat("قائمة مستخدمي VIP:")
                        chunks = [self.user_list[i:i+10] for i in range(0, len(self.user_list), 10)]
                        for chunk in chunks:
                            user_list_str = "\n".join([f"{i+1}. @{username}" for i, username in enumerate(chunk)])
                            await self.highrise.chat(user_list_str)
                    else:
                        await self.highrise.chat("قائمة VIP فارغة حالياً")

            if message.lower() == "r" and user.username.lower() in [u.lower() for u in self.user_list]:
                room_users = await self.highrise.get_room_users()
                for u_obj, pos in room_users.content:
                    try:
                        await self.highrise.react("heart", u_obj.id)
                        await asyncio.sleep(0.01)
                    except Exception as e:
                        logging.error(f"فشل في إرسال قلب لـ {u_obj.username}: {e}")
                return

            if message.lower().startswith("h @"):
                target_username = message.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                target_found = False

                for u_obj, pos in room_users.content:
                    if u_obj.username.lower() == target_username.lower():
                        for _ in range(15):
                            try:
                                await self.highrise.react("heart", u_obj.id)
                                await asyncio.sleep(0.01)
                            except Exception as e:
                                logging.error(f"فشل في إرسال قلب لـ {u_obj.username}: {e}")
                        target_found = True
                        break

                if not target_found:
                    await self.highrise.chat(f"المستخدم @{target_username} غير موجود في الغرفة")
                return

            if message.lower().startswith("علق") and await self.is_user_allowed(user):
                target_username = message.split("@")[-1].strip()
                room_users = await self.highrise.get_room_users()
                user_info = next((info for info in room_users.content if info[0].username.lower() == target_username.lower()), None)

                if user_info:
                    target_user_obj, initial_position = user_info
                    task = asyncio.create_task(self.reset_target_position(target_user_obj, initial_position))

                    if target_user_obj.id not in self.position_tasks:
                        self.position_tasks[target_user_obj.id] = []
                    self.position_tasks[target_user_obj.id].append(task)

            elif message.lower().startswith("حرر") and await self.is_user_allowed(user):
                target_username = message.split("@")[-1].strip()
                room_users = await self.highrise.get_room_users()
                target_user_obj = next((user_obj for user_obj, _ in room_users.content if user_obj.username.lower() == target_username.lower()), None)

                if target_user_obj:
                    tasks = self.position_tasks.pop(target_user_obj.id, [])
                    for task in tasks:
                        task.cancel()
                    logging.info(f"Breaking position monitoring loop for {target_username}")
                else:
                    logging.warning(f"User {target_username} not found in the room.")

            if message.startswith("ik"):
                target_username = message.split("@")[-1].strip()
                await self.userinfo(user, target_username)

            if message.startswith("+x") or message.startswith("-x"):
                await self.adjust_position(user, message, 'x')
            elif message.startswith("+y") or message.startswith("-y"):
                await self.adjust_position(user, message, 'y')
            elif message.startswith("+z") or message.startswith("-z"):
                await self.adjust_position(user, message, 'z')

            allowed_commands = ["بدل", "de", "değiş", "değis", "degiş"]
            if any(message.lower().startswith(command) for command in allowed_commands) and await self.is_user_allowed(user):
                target_username = message.split("@")[-1].strip()

                if target_username not in self.user_list:
                    await self.switch_users(user, target_username)
                else:
                    logging.info(f"{target_username} is in the exclusion list and won't be affected by the switch.")

            if message.lower().startswith("تبع") or message.lower().startswith("tp"):
                target_username = message.split("@")[-1].strip()
                await self.teleport_to_user(user, target_username)

            if message.lower().startswith("روح") or message.lower().startswith("tel"):
                target_username = message.split("@")[-1].strip()
                if user.username.lower() in [u.lower() for u in self.user_list]:
                    await self.teleport_to_user(user, target_username)
                else:
                    await self.highrise.chat("ليس لديك صلاحية استخدام هذا الأمر!")

            if message.lower().startswith("هات") or message.lower().startswith("جيب") or message.lower().startswith("br"):
                target_username = message.split("@")[-1].strip()
                if user.username.lower() in [u.lower() for u in self.user_list]:
                    await self.teleport_user_next_to(target_username, user)
                else:
                    await self.highrise.chat("ليس لديك صلاحية استخدام هذا الأمر!")

            if message.lower().startswith("--") and await self.is_user_allowed(user):
                parts = message.split()
                if len(parts) == 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    target_user = None

                    room_users = (await self.highrise.get_room_users()).content
                    for room_user, _ in room_users:
                        if room_user.username.lower() == target_username and room_user.username.lower() not in self.user_list:
                            target_user = room_user
                            break

                    if target_user:
                        try:
                            kl = Position(random.randint(0, 40), random.randint(0, 40), random.randint(0, 40))
                            await self.teleport(target_user, kl)
                        except Exception as e:
                            logging.error(f"An error occurred while teleporting: {e}")
                    else:
                        logging.warning(f"User '{target_username}' not found in room.")

            if message.lower() == "full rtp" or message.lower() == "برةتلوىوتلل":
                if user.id not in self.kus:
                    self.kus[user.id] = False

                if not self.kus[user.id]:
                    self.kus[user.id] = True

                    try:
                        while self.kus.get(user.id, False):
                            kl = Position(random.randint(0, 29), random.randint(0, 29), random.randint(0, 29))
                            await self.teleport(user, kl)
                            await asyncio.sleep(0.7)
                    except Exception as e:
                        logging.error(f"Teleport error: {e}")
                    finally:
                        self.kus[user.id] = False

            if message.lower() == "توقف" or message.lower() == "stop":
                if user.id in self.kus:
                    self.kus[user.id] = False

            if message.lower().startswith("برونلبماعب") and await self.is_user_allowed(user):
                target_username = message.split("@")[-1].strip().lower()

                if target_username not in self.user_list:
                    room_users = (await self.highrise.get_room_users()).content
                    target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

                    if target_user:
                        if target_user.id not in self.is_teleporting_dict:
                            self.is_teleporting_dict[target_user.id] = True

                            try:
                                while self.is_teleporting_dict.get(target_user.id, False):
                                    kl = Position(random.randint(0, 39), random.randint(0, 29), random.randint(0, 39))
                                    await self.teleport(target_user, kl)
                                    await asyncio.sleep(1)
                            except Exception as e:
                                logging.error(f"An error occurred while teleporting: {e}")
                            finally:
                                self.is_teleporting_dict.pop(target_user.id, None)
                                final_position = Position(4.0, 0.0, 9.5, "FrontRight")
                                await self.teleport(target_user, final_position)

            if message.lower().startswith("وقف") and await self.is_user_allowed(user):
                target_username = message.split("@")[-1].strip().lower()

                room_users = (await self.highrise.get_room_users()).content
                target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

                if target_user:
                    self.is_teleporting_dict.pop(target_user.id, None)

            if message.lower().startswith("طرد") and await self.is_user_allowed(user):
                parts = message.split()
                if len(parts) != 2:
                    return
                if "@" not in parts[1]:
                    username = parts[1]
                else:
                    username = parts[1][1:]

                room_users = (await self.highrise.get_room_users()).content
                for room_user, pos in room_users.content:
                    if room_user.username.lower() == username.lower():
                        user_id = room_user.id
                        banned_username = room_user.username
                        break

                if "user_id" not in locals():
                    return

                try:
                    await self.highrise.moderate_room(user_id, "kick")
                    self.log_ban_action(user.username, banned_username)
                    await self.highrise.chat(f"تم طرد @{banned_username} بواسطة @{user.username}")
                except Exception as e:
                    logging.error(f"Error in kick command: {e}")
                    return

            if "@" in message:
                parts = message.split("@")
                if len(parts) < 2:
                    return

                emote_name = parts[0].strip()
                target_username = parts[1].strip()

                if any(dance[1].lower() == emote_name.lower() for dance in self.dance_list):
                    response = await self.highrise.get_room_users()
                    users = [content[0] for content in response.content]
                    usernames = [user.username.lower() for user in users]

                    if target_username not in usernames:
                        return

                    user_id = next((u.id for u in users if u.username.lower() == target_username), None)
                    if not user_id:
                        return

                    await self.handle_emote_command(user.id, emote_name)
                    await self.handle_emote_command(user_id, emote_name)

            for dance in self.dance_list:
                if message.lower() == dance[1].lower():
                    try:
                        await self.start_continuous_dance(user, dance[2])
                    except Exception as e:
                        logging.error(f"Error sending emote: {e}")

            if message.lower().startswith("dcbbjdc ") and await self.is_user_allowed(user):
                emote_name = message.replace("cvbccvbnn ", "").strip()
                if any(dance[1].lower() == emote_name.lower() for dance in self.dance_list):
                    emote_to_send = next(d[2] for d in self.dance_list if d[1].lower() == emote_name.lower())
                    room_users = (await self.highrise.get_room_users()).content
                    tasks = []
                    for room_user, _ in room_users:
                        tasks.append(self.send_emote_safe(emote_to_send, room_user.id))
                    try:
                        await asyncio.gather(*tasks)
                    except Exception as e:
                        error_message = f"Error sending emotes: {e}"
                        await self.highrise.send_whisper(user.id, error_message)
                else:
                    await self.highrise.send_whisper(user.id, "Invalid emote name: {}".format(emote_name))

            message = message.strip().lower()

            try:
                if message.lstrip().startswith(("اسحر")):
                    response = await self.highrise.get_room_users()
                    users = [content[0] for content in response.content]
                    usernames = [user.username.lower() for user in users]
                    parts = message[1:].split()
                    args = parts[1:]

                    if len(args) >= 1 and args[0][0] == "@" and args[0][1:].lower() in usernames:
                        user_id = next((u.id for u in users if u.username.lower() == args[0][1:].lower()), None)

                        if message.lower().startswith("اسحر"):
                            await self.highrise.send_emote("emote-telekinesis", user.id)
                            await self.highrise.send_emote("emote-gravity", user_id)
            except Exception as e:
                logging.error(f"An error occurred: {e}")

            if message.startswith("rd") or message.startswith("رقصات"):
                try:
                    dance = random.choice(self.dance_list)
                    await self.start_continuous_dance(user, dance[2])
                except Exception as e:
                    logging.error(f"Error sending dance emote: {e}")

        except Exception as e:
            logging.error(f"Error in on_chat: {e}")

    async def on_whisper(self, user: User, message: str) -> None:
        """عند استقبال رسالة همس"""
        if await self.is_user_allowed(user) and message.startswith(''):
            try:
                xxx = message[0:]
                await self.highrise.chat(xxx)
            except Exception as e:
                logging.error(f"Error in whisper handling: {e}")

    async def is_user_allowed(self, user: User) -> bool:
        """التحقق من صلاحيات المستخدم"""
        try:
            user_privileges = await self.highrise.get_room_privilege(user.id)
            return user_privileges.moderator or user.username.lower() in [u.lower() for u in [ "7_e","XQ5"]]
        except Exception as e:
            logging.error(f"Error checking user privileges: {e}")
            return False

    async def moderate_room(
        self,
        user_id: str,
        action: Literal["طرد", "ban", "unban", "mute"],
        action_length: int | None = None,
    ) -> None:
        """إدارة الغرفة"""
        pass

    async def userinfo(self, user: User, target_username: str) -> None:
        """عرض معلومات المستخدم"""
        try:
            user_info = await self.webapi.get_users(username=target_username, limit=1)

            if not user_info.users:
                await self.highrise.chat("Kullanıcı bulunamadı, lütfen geçerli bir kullanıcı belirtin")
                return

            user_id = user_info.users[0].user_id
            user_info = await self.webapi.get_user(user_id)

            number_of_followers = user_info.user.num_followers
            number_of_friends = user_info.user.num_friends
            country_code = user_info.user.country_code
            bio = user_info.user.bio
            active_room = user_info.user.active_room
            crew = user_info.user.crew
            number_of_following = user_info.user.num_following
            joined_at = user_info.user.joined_at.strftime("%d/%m/%Y %H:%M:%S")

            joined_date = user_info.user.joined_at.date()
            today = datetime.now().date()
            days_played = (today - joined_date).days

            last_login = user_info.user.last_online_in.strftime("%d/%m/%Y %H:%M:%S") if user_info.user.last_online_in else "Son giriş bilgisi mevcut değil"

            await self.highrise.chat(f"""اسم المستخدم {target_username}\n عدد المتابعين: {number_of_followers}\n عدد الأصدقاء: {number_of_friends}\n انضم منذ: {joined_at}\n عدد ايام اللعب: {days_played}""")
        except Exception as e:
            logging.error(f"Error getting user info: {e}")
            await self.highrise.chat("حدث خطأ أثناء جلب معلومات المستخدم")

    async def follow(self, user: User, message: str = ""):
        """متابعة المستخدم"""
        self.following_user = user
        while self.following_user == user:
            room_users = (await self.highrise.get_room_users()).content
            for room_user, position in room_users:
                if room_user.id == user.id:
                    user_position = position
                    break
            if user_position is not None and isinstance(user_position, Position):
                nearby_position = Position(user_position.x + 1.0, user_position.y, user_position.z)
                await self.highrise.walk_to(nearby_position)

            await asyncio.sleep(0.5)

    async def adjust_position(self, user: User, message: str, axis: str) -> None:
        """ضبط موضع المستخدم"""
        try:
            adjustment = int(message[2:])
            if message.startswith("-"):
                adjustment *= -1

            room_users = await self.highrise.get_room_users()
            user_position = None

            for user_obj, user_position in room_users.content:
                if user_obj.id == user.id:
                    break

            if user_position:
                new_position = None

                if axis == 'x':
                    new_position = Position(user_position.x + adjustment, user_position.y, user_position.z, user_position.facing)
                elif axis == 'y':
                    new_position = Position(user_position.x, user_position.y + adjustment, user_position.z, user_position.facing)
                elif axis == 'z':
                    new_position = Position(user_position.x, user_position.y, user_position.z + adjustment, user_position.facing)
                else:
                    logging.warning(f"Unsupported axis: {axis}")
                    return

                await self.teleport(user, new_position)

        except ValueError:
            logging.warning("Invalid adjustment value. Please use +x/-x, +y/-y, or +z/-z followed by an integer.")
        except Exception as e:
            logging.error(f"An error occurred during position adjustment: {e}")

    async def switch_users(self, user: User, target_username: str) -> None:
        """تبديل أماكن المستخدمين"""
        try:
            room_users = await self.highrise.get_room_users()

            maker_position = None
            for maker_user, maker_position in room_users.content:
                if maker_user.id == user.id:
                    break

            target_position = None
            for target_user, position in room_users.content:
                if target_user.username.lower() == target_username.lower():
                    target_position = position
                    break

            if maker_position and target_position:
                await self.teleport(user, Position(target_position.x + 0.0001, target_position.y, target_position.z, target_position.facing))
                await self.teleport(target_user, Position(maker_position.x + 0.0001, maker_position.y, maker_position.z, maker_position.facing))

        except Exception as e:
            logging.error(f"An error occurred during user switch: {e}")

    async def teleport(self, user: User, position: Position):
        """نقل المستخدم إلى موضع معين"""
        try:
            await self.highrise.teleport(user.id, position)
        except Exception as e:
            logging.error(f"Caught Teleport Error: {e}")

    async def teleport_to_user(self, user: User, target_username: str) -> None:
        """النقل إلى مستخدم معين"""
        try:
            room_users = await self.highrise.get_room_users()
            for target, position in room_users.content:
                if target.username.lower() == target_username.lower():
                    z = position.z
                    new_z = z - 1
                    await self.teleport(user, Position(position.x, position.y, new_z, position.facing))
                    break
        except Exception as e:
            logging.error(f"An error occurred while teleporting to {target_username}: {e}")

    async def teleport_user_next_to(self, target_username: str, requester_user: User) -> None:
        """جلب مستخدم إلى جانب مستخدم آخر"""
        try:
            room_users = await self.highrise.get_room_users()
            requester_position = None
            for user, position in room_users.content:
                if user.id == requester_user.id:
                    requester_position = position
                    break

            for user, position in room_users.content:
                if user.username.lower() == target_username.lower():
                    z = requester_position.z
                    new_z = z + 1
                    await self.teleport(user, Position(requester_position.x, requester_position.y, new_z, requester_position.facing))
                    break
        except Exception as e:
            logging.error(f"An error occurred while teleporting {target_username} next to {requester_user.username}: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        """عند إرسال تيب"""
        message = f"{sender.username} tarafından {receiver.username}  {tip.amount} 🎁 Thanks so much 🎁."
        await self.highrise.chat(message)

    async def reset_target_position(self, target_user_obj: User, initial_position: Position) -> None:
        """إعادة تعيين موضع المستخدم"""
        try:
            while True:
                room_users = await self.highrise.get_room_users()
                current_position = next((position for user, position in room_users.content if user.id == target_user_obj.id), None)

                if current_position and current_position != initial_position:
                    await self.teleport(target_user_obj, initial_position)

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"An error occurred during position monitoring: {e}")

    async def run(self, room_id, token) -> None:
        """تشغيل البوت"""
        while True:
            try:
                await __main__.main(self, room_id, token)
            except Exception as e:
                logging.error(f"Connection error, retrying in 5 seconds: {e}")
                await asyncio.sleep(5)

class WebServer():
    """خادم ويب للحفاظ على تشغيل البوت"""
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        self.request_count = 0

        @self.app.route('/')
        def index() -> str:
            self.request_count += 1
            if self.request_count % 100 == 0:
                logging.info(f"Health check request #{self.request_count}")
            return "Alive"

    def run(self) -> None:
        self.app.run(host='0.0.0.0', port=8080, threaded=True)

    def keep_alive(self):
        t = Thread(target=self.run)
        t.daemon = True
        t.start()

class RunBot():
    """فئة تشغيل البوت الرئيسية"""
    room_id = "677c10f08c680c76c2d0d446"
    bot_token = "a940130b6ffca3432c6533aea1f9ac569d86e9209de436f46526c07ed2c99606"
    bot_file = "main"
    bot_class = "Bot"

    def __init__(self) -> None:
        self.definitions = [
            BotDefinition(
                getattr(import_module(self.bot_file), self.bot_class)(),
                self.room_id, self.bot_token)
        ]

    def run_loop(self) -> None:
        while True:
            try:
                arun(main(self.definitions))
            except Exception as e:
                import traceback
                logging.error("Caught an exception:")
                traceback.print_exc()
                time.sleep(1)
                continue

if __name__ == "__main__":
    WebServer().keep_alive()
    RunBot().run_loop()