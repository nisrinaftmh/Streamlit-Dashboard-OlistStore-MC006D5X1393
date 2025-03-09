import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Dashboard Analisis dan Visualisasi Data E-Commerce Olist Store Brazil (2016-2018)")

# Path ke file CSV 
pesanan_df = pd.read_csv("E-Commerce Public Dataset/orders_dataset.csv")
barangDibeli_df = pd.read_csv("E-Commerce Public Dataset/order_items_dataset.csv")
produk_df = pd.read_csv("E-Commerce Public Dataset/products_dataset.csv")
proCa_df = pd.read_csv("E-Commerce Public Dataset/product_category_name_translation.csv")
customer_df = pd.read_csv("E-Commerce Public Dataset/customers_dataset.csv")
pay_df = pd.read_csv("E-Commerce Public Dataset/order_payments_dataset.csv")

# Fungsi untuk mengisi missing values dengan mean/mode
def fill_missing_with_mean(df):
    for col in df.select_dtypes(include=np.number):
        df[col] = df[col].fillna(df[col].mean())
    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].fillna(df[col].mode()[0])
    return df

# Bersihkan data
produk_df = fill_missing_with_mean(produk_df)
barangDibeli_df = fill_missing_with_mean(barangDibeli_df)
pesanan_df = fill_missing_with_mean(pesanan_df)
proCa_df = fill_missing_with_mean(proCa_df)
customer_df = fill_missing_with_mean(customer_df)
pay_df = fill_missing_with_mean(pay_df)

# Gabungkan data
df = pd.merge(pesanan_df, barangDibeli_df, on='order_id', how='inner')
df = pd.merge(df, produk_df, on='product_id', how='inner')
df = pd.merge(df, proCa_df, on='product_category_name', how='left')

# Gunakan nama kategori produk dalam bahasa Inggris
df['product_category_name'] = df['product_category_name_english']
df.drop('product_category_name_english', axis=1, inplace=True)

# Konversi tanggal
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Filter tahun 2016-2018
df = df[(df['order_purchase_timestamp'].dt.year >= 2016) & (df['order_purchase_timestamp'].dt.year <= 2018)]

# Top 10 kategori produk terlaris
category_counts = df['product_category_name'].value_counts().head(10)

st.subheader("Top 10 Best-Selling Product Categories (2016-2018)")
fig, ax = plt.subplots(figsize=(15, 6))
sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax)
ax.set_title('Top 10 Best-Selling Product Categories (2016-2018)')
ax.set_xlabel('Product Category')
ax.set_ylabel('Number of Purchases')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

for i, v in enumerate(category_counts.values):
    ax.text(i, v + 5, str(v), ha='center', fontsize=12, fontweight='bold')

st.pyplot(fig)


st.text("""Secara garis besar, hasil pola yang didapatkan pada grafik visualisasi data yang didapatkan, dalam periode 3 tahun terakhir (2O16 - 2018) Olist Store milik Brazil memiliki beberapa kategori produk yang sering dibeli dan diminati oleh konsumen mereka diantaranya

1. pada tabel bed_bath_table yang merupakan kategori perabotan untuk ruangan di rumah, pada grafik dapat kita lihat bahwa terdapat kurang lebih dari 12718 lebih pembelian yang menunjukkan tingginya minat konsumen pada barang barang khusus untuk di kamar tidur dan kamar mandi selama 3 tahun terakhir

2. pada tabel health_beauty kita dapat melihat bahwa jumlah pembelian produk terdapat pada kisaran kurang lebih 9670 pembelian oleh konsumen dimana hal ini menunjukkan ketertarikan tinggi pada kategori produk kecantikan dan perawatan diri oleh konsumen

3. sport_leisure (peralatan olahraga) menempati posisi ketiga dengan pembelian kategori produk tersebut sebanyak 8641 lebih pembelian

4. Furniture_decor (Furnitur dan dekorasi) menempati posisi keempat dengan pembelian kategori produk tersebut sebanyak kurang lebih 8334 pembelian

5. computers_accessories melengkapi lima besar dengan sekitar pembelian 7827 kategori produk tersebut, dimana hal ini menunjukkan permintaan yang konsisten untuk produk elektronik atau aksesoris komputer.

6. Kategori "housewares", "watches_gifts", "telephony", "garden_tools", dan "auto" menempati posisi 6-10 dengan jumlah pembelian yang menurun secara bertahap dari sekitar 6900 hingga 4000 pembelian.

Dalam periode 2016-2018, Olist Store di Brazil menunjukkan pola pembelian yang tinggi pada beberapa kategori produk. **Kategori "bed_bath_table" menjadi yang paling diminati**, diikuti oleh **health_beauty, sports_leisure, furniture_decor, dan computers_accessories**. Produk dalam kategori ini memiliki permintaan yang konsisten dan tinggi. Sementara itu, kategori seperti **housewares, watches_gifts, telephony, garden_tools, dan auto** masih memiliki peminat tetapi dengan jumlah pembelian yang lebih rendah.  

Dari pola ini, strategi pemasaran bisa difokuskan pada kategori produk yang paling diminati dengan **peningkatan stok, promosi, dan diskon** untuk mempertahankan serta meningkatkan jumlah pembelian. Selain itu, kategori dengan penjualan lebih rendah bisa diberikan strategi pemasaran khusus untuk meningkatkan daya tariknya.""")


# Analisis pola waktu pembelian
df['day_of_week'] = df['order_purchase_timestamp'].dt.dayofweek
df['hour_of_day'] = df['order_purchase_timestamp'].dt.hour
df['month'] = df['order_purchase_timestamp'].dt.month
df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

st.subheader("Purchase Frequency by Day of Week")
fig, ax = plt.subplots(figsize=(10, 5))
day_counts = df['day_of_week'].value_counts().sort_index()
sns.barplot(x=day_counts.index, y=day_counts.values, ax=ax)

for i, v in enumerate(day_counts.values):
    ax.text(i, v + 5, str(v), ha='center', fontsize=12, fontweight='bold')

st.pyplot(fig)

st.subheader("Purchase Frequency: Weekday vs. Weekend")
fig, ax = plt.subplots(figsize=(8, 6))
weekend_counts = df['is_weekend'].value_counts().sort_index()
sns.barplot(x=weekend_counts.index, y=weekend_counts.values, ax=ax)

for i, v in enumerate(weekend_counts.values):
    ax.text(i, v + 5, str(v), ha='center', fontsize=12, fontweight='bold')

st.pyplot(fig)

st.text("""Dalam frekuensi belanja konsumen perminggu pada diagram diatas dapat dilihat bahwa konsumen lebih sering berbelanja di hari kerja (senin-jumat) dibandingkan hari libur, tingginya aktivitas berbelanja oleh konsumen di hari kerja kemungkinan karena banyak kebutuhan yang diperlukan seperti misalnya kebutuhan kantor yang dibutuhkan untuk rutinitas harian, selain itu kebanyakan toko beroperasional di hari kerja yang mengakibatkan tingginya angka berbelanja di hari kerja.""")

st.subheader("Purchase Frequency by Hour of Day")
fig, ax = plt.subplots(figsize=(10, 5))
hour_counts = df['hour_of_day'].value_counts().sort_index()
sns.barplot(x=hour_counts.index, y=hour_counts.values, ax=ax)

for i, v in enumerate(hour_counts.values):
    ax.text(i, v + 5, str(v), ha='center', fontsize=12, fontweight='bold')

st.pyplot(fig)

st.text("""Dalam frekuensi belanja konsumen per hari berdasarkan jam dapat dilihat bahwa jumlah invoice pesanan produk yang masuk tinggi mulai pukul 10.00-21.00 dan menurun pada pukul 22.00 keatas mulai menurun dan tingkat berbelanja pukul 02.00-06.00 cenderung rendah kemungkinan aktivitas belanja oleh konsumen. Hal ini menunjukkan pada jam sibuk mulai jam 10.00-20.00 adalah selang waktu orang beristirahat dan memiliki waktu luang""")


st.subheader("Purchase Frequency by Month")
fig, ax = plt.subplots(figsize=(10, 5))
month_counts = df['month'].value_counts().sort_index()
sns.barplot(x=month_counts.index, y=month_counts.values, ax=ax)

for i, v in enumerate(month_counts.values):
    ax.text(i, v + 5, str(v), ha='center', fontsize=12, fontweight='bold')

st.pyplot(fig)

st.text(""" Dalam frekuensi belanja konsumen per bulan dapat kita lihat bahwa kegiatan berbelanja berada pada puncaknya di bulan mei hingga agustus. Hal ini kemungkinan terjadi karena di brazil sendiri terjadi musim dingin sekitar bulan juni-agustus yang mengakibatkan masyarakatnya cenderung berbelanja online dibandingkan pergi ke toko fisik karena keterbatasan berkegiatan di musim salju/musim dingin.""")


st.subheader("Purchase Frequency Heatmap (Day of Week vs. Hour of Day)")
heatmap_data = df.pivot_table(index='day_of_week', columns='hour_of_day', values='order_id', aggfunc='count')
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='viridis', ax=ax)

st.pyplot(fig)

st.text("""Pola waktu pembelian konsumen menunjukkan bahwa transaksi lebih sering terjadi pada hari kerja (Senin–Jumat) dibandingkan hari libur. Hal ini kemungkinan disebabkan oleh kebutuhan rutin, seperti perlengkapan kantor yang harus dibeli untuk menunjang aktivitas harian. Selain itu, banyak toko yang beroperasi penuh pada hari kerja, sehingga konsumen lebih aktif berbelanja pada periode tersebut dibandingkan akhir pekan atau hari libur. Jika dilihat berdasarkan jam transaksi dalam sehari, jumlah pesanan mulai meningkat dari pukul 10.00 dan mencapai puncaknya pada pukul 21.00. Setelah pukul 22.00, tingkat transaksi mulai menurun drastis, dan pada pukul 02.00–06.00 aktivitas belanja cenderung sangat rendah. Pola ini menunjukkan bahwa konsumen cenderung melakukan pembelian pada jam istirahat dan waktu luang, terutama pada rentang 10.00–20.00 yang menjadi periode dengan tingkat transaksi tertinggi.Berdasarkan pola ini, terdapat beberapa strategi yang dapat diterapkan oleh Olist untuk meningkatkan penjualan. Salah satunya adalah dengan menargetkan promosi dan iklan pada jam 10.00–20.00 di hari kerja, mengingat periode ini memiliki jumlah transaksi tertinggi dan potensi keterlibatan konsumen yang lebih besar.""")
