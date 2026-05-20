import pandas as pd

manual = {
    "fish1_id": [864691128615288811, 864691128618512214, 864691128631576966],
    "contralateral": [False, False, False],
    "nt_manual": ["na", "na", "na"],
    "id": [87071, 169547, 166285],
    "nt_cave": ["na", "na", "na"],
}

df_pretec_raw = pd.DataFrame(manual)

df_pretec_raw.to_csv("/Users/aljoscha/Downloads/neurons22.csv", index=False)

# ruths
# df_read = pd.read_csv('/Users/aljoscha/Downloads/neurons22.csv')
# ruths
# x_min_em = 40636
# x_max_em = 44455
#
# y_min_em = 31793
# y_max_em = 36291
#
# z_min_em = 5349
# z_max_em = 6294