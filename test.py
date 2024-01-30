import base64
import io

import telegram
import pandas as pd
import psycopg2
import seaborn as sns
import matplotlib.pyplot as plt
import asyncio

bot_token = '6552966095:AAGkq7DxCluoE69FtvZgP3n07JGGYPzwsCo'


def check_anomaly(df, metric, a=4, n=5):
    df['q25'] = df[metric].shift(1).rolling(n).quantile(0.25)
    df['q75'] = df[metric].shift(1).rolling(n).quantile(0.75)
    df['igr'] = df['q75'] - df['q25']
    df['up'] = df['q75'] - a*df['igr']
    df['low'] = df['q25'] - a*df['igr']

    df['up'] = df['up'].rolling(n, center=True, min_periods=1).mean()
    df['low'] = df['up'].rolling(n, center=True, min_periods=1).mean()

    if df[metric].iloc[-1] < df['low'].iloc[-1] or df[metric].iloc[-1] > df['up'].iloc[-1]:
        is_alert = 1
    else:
        is_alert = 0
    return is_alert, df


async def get_alert(chat=None):
    chat_id = chat or 464674948
    bot = telegram.Bot(token=bot_token)
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="data_feed")

        cur = connection.cursor()
        cur.execute('''
        SELECT
            date_trunc('hour', time) + interval '15 minutes' * floor(date_part('minute', time) / 15) AS ts,
            date(time) AS date,
            to_char(date_trunc('hour', time) + interval '15 minutes' * floor(date_part('minute', time) / 15), 'HH24:MI') AS hm,
            count(DISTINCT user_id) AS users_feed,
            count(*) FILTER (WHERE action = 'view') AS view,
            count(*) FILTER (WHERE action = 'like') AS like
        FROM user_actions
        WHERE time BETWEEN '2023-05-16' AND '2023-05-17'
        GROUP BY ts, date, hm
        ORDER BY ts;
        ''')
        rows = cur.fetchall()

        data = pd.DataFrame(rows, columns=['ts', 'date', 'hm', 'users_feed', 'views', 'likes'])
        print(data)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")

    metrics_list = ["users_feed", "views", "likes"]

    for metric in metrics_list:
        print(metric)
        df = data[['ts', 'date', 'hm', metric]].copy()
        is_alert, df = check_anomaly(df, metric)

        if is_alert == 1:
            msg = (f'Метрика {metric}: текущее значение '
                   f'{df[metric].iloc[-1]} отклонение от последнего значения {abs(1 - df[metric].iloc[-1]/df[metric].iloc[-2])}')

            sns.set(rc={'figure.figsize': (16,10)})
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

            await bot.sendMessage(chat_id=chat_id, text=msg)
            await bot.sendPhoto(chat_id=chat_id, photo=img_base64)
    return


async def main():
    await get_alert()


asyncio.run(main())
