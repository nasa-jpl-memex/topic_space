from bs4 import BeautifulSoup
import pandas as pd


def extract_top_universities(filename):
    with open(filename) as f:
        soup = BeautifulSoup(f)
        universities = []
        for content in soup.body.find("div", id="resultsMain").find_all(class_="sep"):
            score = content.find(class_="t-large t-strong t-constricted").get_text().strip()
            rank = content.find(class_="rankscore-bronze").get_text().strip().rstrip("\n\n      Tie")
            university = content.find(class_="h-taut").get_text().strip()
            country = content.find(class_="t-taut").span.get_text()
            city = content.find(class_="t-taut").find(class_="t-dim t-small").get_text()
            line = [score, rank, university, country, city]
            universities.append(line)

        return universities


def generate_top_uni_csv(filename1, filename2, csv_filename):
    top_ms_uni1 = extract_top_universities(filename1)
    top_ms_uni2 = extract_top_universities(filename2)

    top_ms_uni1_df = pd.DataFrame(top_ms_uni1, columns=["score", "rank", "university", "country", "city"])
    top_ms_uni2_df = pd.DataFrame(top_ms_uni2, columns=["score", "rank", "university", "country", "city"])

    top_ms_uni = pd.concat([top_ms_uni1_df, top_ms_uni2_df], ignore_index=True)
    top_ms_uni.to_csv(path_or_buf=csv_filename, sep="\t")


if __name__ == "__main__":
    # Generate top 20 universities in Material Science from US News ranking site.
    generate_top_uni_csv("data/us-news-top-20-universities-1.html",
                         "data/us-news-top-20-universities-2.html", "output/top_ms_uni.tsv")

    # Generate top 20 chinese universities in Material Science from US News ranking site.
    generate_top_uni_csv("data/us-news-top-20-universities-china-1.html",
                         "data/us-news-top-20-universities-china-2.html", "output/top_ms_china_uni.tsv")
