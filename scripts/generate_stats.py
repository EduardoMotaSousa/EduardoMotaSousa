import json
import os
import urllib.request
import urllib.parse
from html import escape


USERNAME = "EduardoMotaSousa"
OUTPUT_DIR = "dist"

API_URL = "https://api.github.com"


def github_request(endpoint):
    url = API_URL + endpoint

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "EduardoMotaSousa-Profile-Stats",
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def get_user():
    return github_request(f"/users/{USERNAME}")


def get_repositories():
    repositories = []

    page = 1

    while True:
        repos = github_request(
            f"/users/{USERNAME}/repos"
            f"?per_page=100&page={page}&type=owner"
        )

        if not repos:
            break

        repositories.extend(repos)

        if len(repos) < 100:
            break

        page += 1

    return repositories


def get_languages(repository):
    owner = repository["owner"]["login"]
    name = repository["name"]

    return github_request(
        f"/repos/{owner}/{name}/languages"
    )


def format_number(value):
    if value >= 1000:
        return f"{value / 1000:.1f}k"

    return str(value)


def generate_svg(filename, content, width=900, height=300):
    svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}">

    <rect
        width="100%"
        height="100%"
        rx="12"
        fill="#0d1117"
        stroke="#30363d"/>

    {content}

</svg>
"""

    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as file:
        file.write(svg)


def generate_stats(user, repositories):
    total_stars = sum(
        repository["stargazers_count"]
        for repository in repositories
    )

    total_forks = sum(
        repository["forks_count"]
        for repository in repositories
    )

    total_watchers = sum(
        repository["watchers_count"]
        for repository in repositories
    )

    content = f"""
    <text
        x="40"
        y="50"
        fill="#f0f6fc"
        font-family="Arial, sans-serif"
        font-size="24"
        font-weight="bold">
        GitHub Statistics
    </text>

    <text
        x="40"
        y="78"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        @EduardoMotaSousa
    </text>

    <line
        x1="40"
        y1="105"
        x2="860"
        y2="105"
        stroke="#30363d"/>

    <text x="80" y="155"
        fill="#58a6ff"
        font-family="Arial, sans-serif"
        font-size="28"
        font-weight="bold">
        {format_number(user["public_repos"])}
    </text>

    <text x="80" y="180"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        repositories
    </text>

    <text x="280" y="155"
        fill="#58a6ff"
        font-family="Arial, sans-serif"
        font-size="28"
        font-weight="bold">
        {format_number(total_stars)}
    </text>

    <text x="280" y="180"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        stars
    </text>

    <text x="480" y="155"
        fill="#58a6ff"
        font-family="Arial, sans-serif"
        font-size="28"
        font-weight="bold">
        {format_number(total_forks)}
    </text>

    <text x="480" y="180"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        forks
    </text>

    <text x="680" y="155"
        fill="#58a6ff"
        font-family="Arial, sans-serif"
        font-size="28"
        font-weight="bold">
        {format_number(user["followers"])}
    </text>

    <text x="680" y="180"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        followers
    </text>

    <line
        x1="40"
        y1="215"
        x2="860"
        y2="215"
        stroke="#30363d"/>

    <text x="40" y="250"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        Automatically generated from GitHub API
    </text>
    """

    generate_svg(
        "stats.svg",
        content,
        900,
        290,
    )


def generate_languages(repositories):
    languages = {}

    for repository in repositories:
        if repository["fork"]:
            continue

        try:
            repository_languages = get_languages(repository)
        except Exception:
            continue

        for language, amount in repository_languages.items():
            languages[language] = languages.get(language, 0) + amount

    languages = sorted(
        languages.items(),
        key=lambda item: item[1],
        reverse=True
    )[:6]

    total = sum(value for _, value in languages)

    content = """
    <text
        x="40"
        y="50"
        fill="#f0f6fc"
        font-family="Arial, sans-serif"
        font-size="24"
        font-weight="bold">
        Languages
    </text>
    """

    y = 90

    for language, amount in languages:
        percentage = (amount / total) * 100 if total else 0

        bar_width = int(650 * percentage / 100)

        content += f"""
        <text
            x="40"
            y="{y}"
            fill="#f0f6fc"
            font-family="Arial, sans-serif"
            font-size="14">
            {escape(language)}
        </text>

        <rect
            x="150"
            y="{y - 13}"
            width="650"
            height="12"
            rx="6"
            fill="#21262d"/>

        <rect
            x="150"
            y="{y - 13}"
            width="{bar_width}"
            height="12"
            rx="6"
            fill="#58a6ff"/>

        <text
            x="820"
            y="{y}"
            fill="#8b949e"
            font-family="Arial, sans-serif"
            font-size="13">
            {percentage:.1f}%
        </text>
        """

        y += 40

    generate_svg(
        "languages.svg",
        content,
        900,
        350,
    )


def generate_project(repository, filename):
    name = escape(repository["name"])
    description = escape(
        repository["description"] or "No description provided."
    )

    language = escape(
        repository["language"] or "Various"
    )

    stars = repository["stargazers_count"]

    content = f"""
    <text
        x="35"
        y="48"
        fill="#58a6ff"
        font-family="Arial, sans-serif"
        font-size="22"
        font-weight="bold">
        {name}
    </text>

    <text
        x="35"
        y="85"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="14">
        {description[:90]}
    </text>

    <text
        x="35"
        y="125"
        fill="#f0f6fc"
        font-family="Arial, sans-serif"
        font-size="13">
        {language}
    </text>

    <text
        x="180"
        y="125"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="13">
        ★ {stars}
    </text>
    """

    generate_svg(
        filename,
        content,
        500,
        160,
    )


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching GitHub profile...")
    user = get_user()

    print("Fetching repositories...")
    repositories = get_repositories()

    print("Generating statistics...")
    generate_stats(user, repositories)

    print("Generating languages...")
    generate_languages(repositories)

    projects = {
        "University-Classes": "university-classes.svg",
        "Calculo-de-Figurinhas": "calculo-de-figurinhas.svg",
    }

    print("Generating project cards...")

    for repository in repositories:
        if repository["name"] in projects:
            generate_project(
                repository,
                projects[repository["name"]],
            )

    print("Done.")


if __name__ == "__main__":
    main()
