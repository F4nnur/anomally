import base64

from methods.methods import check_anomaly
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io


async def get_data(db: Session):
    query = text('''SELECT
            date_trunc('hour', time) + interval '15 minutes' * floor(date_part('minute', time) / 15) AS ts,
            date(time) AS date,
            to_char(date_trunc('hour', time) + interval '15 minutes' * floor(date_part('minute', time) / 15), 'HH24:MI') AS hm,
            count(DISTINCT user_id) AS users_feed,
            count(*) FILTER (WHERE action = 'view') AS view,
            count(*) FILTER (WHERE action = 'like') AS like
        FROM user_actions
        WHERE time BETWEEN '2023-05-16' AND '2023-05-17'
        GROUP BY ts, date, hm
        ORDER BY ts;''')

    res = db.execute(query).fetchall()
    data = pd.DataFrame(res, columns=['ts', 'date', 'hm', 'users_feed', 'views', 'likes'])
    metrics_list = ["users_feed", "views", "likes"]

    results = []

    for metric in metrics_list:
        df = data[['ts', 'date', 'hm', metric]].copy()
        is_alert, df = check_anomaly(df, metric)

        if is_alert == 1:
            msg = (f'Метрика {metric}: текущее значение '
                   f'{df[metric].iloc[-1]} отклонение от последнего значения {abs(1 - df[metric].iloc[-1] / df[metric].iloc[-2])}')

            sns.set(rc={'figure.figsize': (16, 10)})
            plt.tight_layout()
            ax = sns.lineplot(x=df['ts'], y=df[metric], label='metric')
            ax = sns.lineplot(x=df['ts'], y=df['up'], label='up')
            ax = sns.lineplot(x=df['ts'], y=df['low'], label='low')

            for ind, label in enumerate(ax.get_xticklabels()):
                if ind % 2 == 0:
                    label.set_visible(True)
                else:
                    label.set_visible(False)

            ax.set(xlabel='time')
            ax.set(ylabel=metric)

            ax.set_title(metric)
            ax.set(ylim=(0, None))

            plot_object = io.BytesIO()
            ax.figure.savefig(plot_object)
            plot_object.seek(0)
            plot_object.name = f'{metric}.png'
            plt.close()
            img_str = plot_object.getvalue()
            img_base64 = base64.b64encode(img_str).decode('utf-8')

            results.append({'message': msg, "image": img_base64})
    return results
