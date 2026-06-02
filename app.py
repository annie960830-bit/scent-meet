from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    df = pd.read_csv("perfumes.csv", encoding="utf-8-sig")
    perfumes = df.to_dict(orient="records")

    return render_template("index.html", perfumes=perfumes)



@app.route("/quiz/1")
def quiz1():
    return render_template("quiz1.html")


@app.route("/quiz/2", methods=["GET", "POST"])
def quiz2():
    purpose = request.form.get("purpose", "")

    return render_template("quiz2.html", purpose=purpose)

@app.route("/quiz/3", methods=["GET", "POST"])
def quiz3():
    purpose = request.form.get("purpose", "")
    occasion = request.form.get("occasion", "")

    return render_template(
        "quiz3.html",
        purpose=purpose,
        occasion=occasion
    )

@app.route("/quiz/4", methods=["GET", "POST"])
def quiz4():
    purpose = request.form.get("purpose", "")
    occasion = request.form.get("occasion", "")
    scent = request.form.get("scent", "")

    return render_template(
        "quiz4.html",
        purpose=purpose,
        occasion=occasion,
        scent=scent
    )

@app.route("/result", methods=["POST"])
def result():
    purpose = request.form.get("purpose", "")
    occasion = request.form.get("occasion", "")
    scent = request.form.get("scent", "")
    price_range = request.form.get("price_range", "")

    conn = sqlite3.connect("perfumes.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    exact_match = False

    sql_exact = """
    SELECT rowid AS id, *
    FROM perfumes
    WHERE 場合 = ?
    AND 香調 = ?
    """

    params = [occasion, scent]

    if price_range == "5000以下":
        sql_exact += " AND 價格 <= ?"
        params.append(5000)

    elif price_range == "5000以上":
        sql_exact += " AND 價格 > ?"
        params.append(5000)

    cursor.execute(sql_exact, params)
    perfumes = [dict(row) for row in cursor.fetchall()]

    if perfumes:
        exact_match = True

    else:
        sql_fallback = """
        SELECT rowid AS id, *
        FROM perfumes
        WHERE 香調 = ?
        """

        fallback_params = [scent]

        if price_range == "5000以下":
            sql_fallback += " AND 價格 <= ?"
            fallback_params.append(5000)

        elif price_range == "5000以上":
            sql_fallback += " AND 價格 > ?"
            fallback_params.append(5000)

            sql_fallback += """
            ORDER BY 持香度 DESC
            LIMIT 6
            """

            cursor.execute(sql_fallback, fallback_params)
            perfumes = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "result.html",
        perfumes=perfumes,
        purpose=purpose,
        occasion=occasion,
        scent=scent,
        price_range=price_range,
        exact_match=exact_match
    )
@app.route("/perfumes")
def perfumes():
    keyword = request.args.get("keyword", "")

    conn = sqlite3.connect("perfumes.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if keyword:
        sql = """
        SELECT rowid AS id, *
        FROM perfumes
        WHERE 香水名稱 LIKE ?
        OR 品牌 LIKE ?
        OR 香調 LIKE ?
        OR 場合 LIKE ?
        OR 季節 LIKE ?
        """
        like_keyword = "%" + keyword + "%"
        cursor.execute(sql, (
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword
        ))
    else:
        cursor.execute("SELECT rowid AS id, * FROM perfumes")

    perfumes = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "perfumes.html",
        perfumes=perfumes,
        keyword=keyword
    )


@app.route("/perfume/<int:id>")
def perfume_detail(id):
    conn = sqlite3.connect("perfumes.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT rowid AS id, * FROM perfumes WHERE rowid = ?",
        (id,)
    )

    perfume = cursor.fetchone()

    conn.close()

    return render_template(
        "perfume_detail.html",
        perfume=dict(perfume)
    )

@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")

    conn = sqlite3.connect("perfumes.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    perfumes = []

    if keyword:
        like_keyword = "%" + keyword + "%"
        cursor.execute("""
            SELECT rowid AS id, *
            FROM perfumes
            WHERE 香水名稱 LIKE ?
               OR 品牌 LIKE ?
               OR 香調 LIKE ?
               OR 場合 LIKE ?
               OR 季節 LIKE ?
        """, (
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword
        ))

        perfumes = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "search.html",
        perfumes=perfumes,
        keyword=keyword
    )

if __name__ == "__main__":
    app.run(debug=True)