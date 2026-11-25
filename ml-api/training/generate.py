from __future__ import annotations

import random

SEED = 42
SAMPLES_PER_CLASS = 3200

DGA_TLDS = ("com", "net", "org", "info", "biz", "ru", "cn", "xyz", "top", "io", "co")
BENIGN_TLDS = (
    "com",
    "com",
    "com",
    "net",
    "org",
    "io",
    "co",
    "de",
    "fr",
    "uk",
    "ca",
    "us",
    "eu",
)

CONSONANTS = "bcdfghjklmnpqrstvwxz"
VOWELS = "aeiou"
ALNUM = "abcdefghijklmnopqrstuvwxyz0123456789"
HEX = "0123456789abcdef"

DGA_WORDS = (
    "alpha", "amber", "angel", "arrow", "baker", "beach", "berry", "black",
    "blade", "bloom", "board", "brick", "bridge", "brown", "brush", "cabin",
    "cable", "candy", "carpet", "castle", "cedar", "chain", "chair", "chalk",
    "charm", "chess", "chill", "cloud", "coast", "coral", "crane", "crown",
    "crystal", "dance", "delta", "denim", "diner", "dolphin", "dragon", "dream",
    "drift", "eagle", "earth", "ember", "fable", "feather", "field", "flame",
    "flint", "forest", "frost", "garden", "ghost", "glass", "globe", "gold",
    "grain", "grape", "green", "grove", "harbor", "hazel", "heart", "honey",
    "horse", "house", "island", "ivory", "jade", "jewel", "jungle", "kite",
    "knife", "ladder", "lake", "lamp", "lantern", "lemon", "light", "linen",
    "lion", "lotus", "lunar", "maple", "marble", "marsh", "meadow", "melon",
    "metal", "mint", "mirror", "moon", "moss", "mountain", "nectar", "night",
    "north", "ocean", "olive", "onyx", "orbit", "orchid", "paint", "paper",
    "pearl", "pepper", "piano", "pillow", "pine", "planet", "plum", "pond",
    "prism", "quartz", "queen", "raven", "reed", "ribbon", "river", "robin",
    "rock", "rose", "ruby", "sail", "sand", "sapphire", "scarlet", "shadow",
    "shell", "silver", "sky", "snow", "solar", "sparrow", "spice", "spring",
    "star", "steel", "stone", "storm", "sun", "swan", "table", "tiger",
    "timber", "topaz", "torch", "tower", "trail", "tulip", "valley", "velvet",
    "violet", "water", "willow", "wind", "winter", "wolf", "wood", "yellow",
)

BENIGN_ADJECTIVES = (
    "bright", "blue", "green", "swift", "smart", "clear", "prime", "global",
    "rapid", "quiet", "solid", "fresh", "modern", "urban", "north", "south",
    "east", "west", "open", "true", "pure", "vivid", "silver", "golden",
    "digital", "cloud", "data", "hyper", "meta", "little", "happy", "sunny",
)

BENIGN_NOUNS = (
    "market", "cloud", "store", "shop", "media", "group", "labs", "works",
    "systems", "solutions", "digital", "studio", "design", "travel", "health",
    "finance", "energy", "food", "home", "garden", "tech", "soft", "link",
    "path", "point", "space", "zone", "hub", "base", "grid", "wave", "peak",
    "river", "stone", "field", "house", "line", "net", "care", "club",
)

BENIGN_BRANDS = (
    "acme", "zenith", "orbit", "nimbus", "pixel", "vertex", "atlas", "nova",
    "lumen", "cobalt", "ember", "fable", "glide", "harbor", "indigo", "jasper",
    "kite", "lotus", "mango", "onyx", "pebble", "quill", "raven", "sable",
    "tundra", "umber", "vista", "willow", "yonder", "zephyr",
)

CURATED_BENIGN = (
    "google.com", "youtube.com", "facebook.com", "baidu.com", "wikipedia.org",
    "qq.com", "amazon.com", "yahoo.com", "yandex.ru", "twitter.com", "live.com",
    "microsoft.com", "instagram.com", "netflix.com", "whatsapp.com", "reddit.com",
    "office.com", "linkedin.com", "tiktok.com", "twitch.tv", "bing.com",
    "ebay.com", "msn.com", "wordpress.com", "apple.com", "imgur.com",
    "stackoverflow.com", "github.com", "gitlab.com", "bitbucket.org",
    "dropbox.com", "box.com", "adobe.com", "salesforce.com", "oracle.com",
    "ibm.com", "intel.com", "nvidia.com", "amd.com", "dell.com", "hp.com",
    "lenovo.com", "samsung.com", "sony.com", "panasonic.com", "lg.com",
    "xiaomi.com", "huawei.com", "alibaba.com", "aliexpress.com", "taobao.com",
    "tmall.com", "jd.com", "weibo.com", "wechat.com", "sohu.com", "sina.com.cn",
    "163.com", "126.com", "bilibili.com", "douyin.com", "kuaishou.com",
    "zhihu.com", "ctrip.com", "meituan.com", "pinduoduo.com", "tencent.com",
    "netease.com", "youku.com", "iqiyi.com", "spotify.com", "soundcloud.com",
    "deezer.com", "pandora.com", "hulu.com", "disneyplus.com", "hbomax.com",
    "primevideo.com", "peacocktv.com", "paramountplus.com", "crunchyroll.com",
    "vimeo.com", "dailymotion.com", "pinterest.com", "tumblr.com", "snapchat.com",
    "telegram.org", "discord.com", "slack.com", "zoom.us", "webex.com",
    "gotomeeting.com", "skype.com", "viber.com", "line.me", "kakao.com",
    "naver.com", "daum.net", "rakuten.co.jp", "yahoo.co.jp", "mercari.com",
    "zozo.jp", "niconico.jp", "mixi.jp", "ameblo.jp", "livedoor.jp",
    "seznam.cz", "wp.pl", "onet.pl", "interia.pl", "allegro.pl", "olx.pl",
    "avito.ru", "mail.ru", "ok.ru", "vk.com", "rambler.ru", "rbc.ru",
    "lenta.ru", "gazeta.ru", "ria.ru", "tass.ru", "bbc.co.uk", "bbc.com",
    "cnn.com", "nytimes.com", "washingtonpost.com", "theguardian.com",
    "stackexchange.com",
    "serverfault.com", "superuser.com", "quora.com", "medium.com", "dev.to",
    "hashnode.com", "substack.com", "ghost.org", "wix.com", "squarespace.com",
    "shopify.com", "etsy.com", "walmart.com", "target.com", "bestbuy.com",
    "costco.com", "homedepot.com", "lowes.com", "ikea.com", "wayfair.com",
    "overstock.com", "newegg.com", "sephora.com", "macys.com", "nordstrom.com",
    "zappos.com", "nike.com", "adidas.com", "puma.com", "underarmour.com",
    "rei.com", "decathlon.com", "booking.com", "expedia.com", "airbnb.com",
    "tripadvisor.com", "kayak.com", "hotels.com", "agoda.com", "trivago.com",
    "skyscanner.com", "uber.com", "lyft.com", "doordash.com", "grubhub.com",
    "ubereats.com", "instacart.com", "postmates.com", "deliveroo.com",
    "just-eat.co.uk", "opentable.com", "yelp.com", "zomato.com", "swiggy.com",
    "paypal.com", "stripe.com", "squareup.com", "visa.com", "mastercard.com",
    "americanexpress.com", "discover.com", "chase.com", "bankofamerica.com",
    "wellsfargo.com", "citibank.com", "hsbc.com", "barclays.co.uk",
    "lloydsbank.com", "natwest.com", "santander.com", "ing.com", "revolut.com",
    "monzo.com", "wise.com", "coinbase.com", "binance.com", "kraken.com",
    "kucoin.com", "bybit.com", "okx.com", "bitfinex.com", "gemini.com",
    "robinhood.com", "etrade.com", "fidelity.com", "schwab.com", "vanguard.com",
    "tdameritrade.com", "interactivebrokers.com", "coinmarketcap.com",
    "coingecko.com", "etherscan.io", "blockchain.com", "bitly.com",
    "tinyurl.com", "change.org", "gofundme.com", "kickstarter.com",
    "indiegogo.com", "patreon.com", "onlyfans.com", "steamcommunity.com",
    "steampowered.com", "epicgames.com", "ea.com", "ubisoft.com", "blizzard.com",
    "riotgames.com", "rockstargames.com", "nintendo.com", "playstation.com",
    "xbox.com", "chess.com", "lichess.org", "duolingo.com", "khanacademy.org",
    "coursera.org", "edx.org", "udemy.com", "udacity.com", "brilliant.org",
    "codecademy.com", "freecodecamp.org", "leetcode.com", "hackerrank.com",
    "codewars.com", "exercism.org", "pluralsight.com", "skillshare.com",
    "masterclass.com", "mit.edu", "harvard.edu", "stanford.edu", "ox.ac.uk",
    "cambridge.org", "berkeley.edu", "caltech.edu", "ethz.ch", "tum.de",
    "who.int", "un.org", "worldbank.org", "imf.org", "nato.int", "europa.eu",
    "whitehouse.gov", "senate.gov", "house.gov", "state.gov", "nasa.gov",
    "noaa.gov", "nih.gov", "cdc.gov", "fda.gov", "usps.com", "irs.gov",
    "gov.uk", "nhs.uk", "weather.com", "accuweather.com", "wunderground.com",
    "timeanddate.com", "dictionary.com", "archive.org", "gutenberg.org",
    "wikimedia.org", "wiktionary.org", "wikihow.com", "imdb.com", "9gag.com",
    "sourceforge.net", "mozilla.org",
    "firefox.com", "duckduckgo.com", "booking.com", "cloudflare.com",
    "digitalocean.com", "heroku.com", "vercel.com", "netlify.com", "npmjs.com",
    "pypi.org", "docker.com", "kubernetes.io", "python.org", "rust-lang.org",
    "golang.org", "nodejs.org", "php.net", "ruby-lang.org", "perl.org",
    "apache.org", "nginx.org", "mysql.com", "postgresql.org", "mongodb.com",
    "redis.io", "elastic.co", "grafana.com", "prometheus.io",
)


def curated_benign_domains() -> list[str]:
    return list(dict.fromkeys(CURATED_BENIGN))


def _random_label(rng: random.Random, alphabet: str, min_len: int, max_len: int) -> str:
    length = rng.randint(min_len, max_len)
    return "".join(rng.choice(alphabet) for _ in range(length))


def _random_alnum(rng: random.Random) -> str:
    return _random_label(rng, ALNUM, 10, 24)


def _hex(rng: random.Random) -> str:
    return rng.choice("abcdef") + _random_label(rng, HEX, 11, 31)


def _consonant_heavy(rng: random.Random) -> str:
    length = rng.randint(10, 22)
    chars = [
        rng.choice(VOWELS) if rng.random() < 0.12 else rng.choice(CONSONANTS)
        for _ in range(length)
    ]
    return "".join(chars)


def _dictionary(rng: random.Random) -> str:
    first, second = rng.sample(DGA_WORDS, 2)
    return first + second


def _mixed(rng: random.Random) -> str:
    kind = rng.randrange(3)
    if kind == 0:
        label = rng.choice(DGA_WORDS) + _random_label(rng, ALNUM, 6, 10)
    elif kind == 1:
        label = f"{_random_label(rng, ALNUM, 5, 9)}-{_random_label(rng, ALNUM, 5, 9)}"
    else:
        label = _hex(rng)[:12] + rng.choice(DGA_WORDS)
    return label


DGA_FAMILIES = (_random_alnum, _hex, _consonant_heavy, _dictionary, _mixed)


def _generate_dga(rng: random.Random, count: int, seen: set[str]) -> list[str]:
    domains: list[str] = []
    while len(domains) < count:
        family = rng.choice(DGA_FAMILIES)
        domain = f"{family(rng)}.{rng.choice(DGA_TLDS)}"
        if domain not in seen:
            seen.add(domain)
            domains.append(domain)
    return domains


def _generate_benign(rng: random.Random, count: int, seen: set[str]) -> list[str]:
    domains: list[str] = []
    while len(domains) < count:
        kind = rng.randrange(4)
        if kind == 0:
            label = rng.choice(BENIGN_BRANDS) + rng.choice(BENIGN_NOUNS)
        elif kind == 1:
            label = f"{rng.choice(BENIGN_ADJECTIVES)}-{rng.choice(BENIGN_NOUNS)}"
        elif kind == 2:
            label = rng.choice(BENIGN_ADJECTIVES) + rng.choice(BENIGN_NOUNS)
        else:
            label = f"{rng.choice(BENIGN_BRANDS)}-{rng.choice(BENIGN_NOUNS)}"
        tld = rng.choice(BENIGN_TLDS)
        if rng.random() < 0.08:
            tld = "co.uk"
        domain = f"{label}.{tld}"
        if domain not in seen:
            seen.add(domain)
            domains.append(domain)
    return domains


def build_dataset(seed: int = SEED, samples_per_class: int = SAMPLES_PER_CLASS):
    rng = random.Random(seed)
    seen: set[str] = set()
    curated = curated_benign_domains()
    seen.update(curated)
    dga = _generate_dga(rng, samples_per_class, seen)
    benign = curated + _generate_benign(rng, samples_per_class - len(curated), seen)
    domains = dga + benign
    labels = [1] * len(dga) + [0] * len(benign)
    return domains, labels
