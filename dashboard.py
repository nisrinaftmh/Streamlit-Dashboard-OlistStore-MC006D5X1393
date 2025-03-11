import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set page config
st.set_page_config(layout="wide", page_title="Analisis E-Commerce Olist")

# Title and description
st.title("Dashboard Analisis dan Visualisasi Data E-Commerce Olist Store Brazil (2016-2018)")
st.markdown("Dashboard ini menampilkan analisis pola belanja konsumen berdasarkan waktu")

# Load data
@st.cache_data
def load_data():
    pesanan_df = pd.read_csv("E-Commerce Public Dataset/orders_dataset.csv")
    barangDibeli_df = pd.read_csv("E-Commerce Public Dataset/order_items_dataset.csv")
    produk_df = pd.read_csv("E-Commerce Public Dataset/products_dataset.csv")
    proCa_df = pd.read_csv("E-Commerce Public Dataset/product_category_name_translation.csv")
    
    df = pd.merge(pesanan_df, barangDibeli_df, on='order_id', how='inner')
    df = pd.merge(df, produk_df, on='product_id', how='inner')
    df = pd.merge(df, proCa_df, on='product_category_name', how='left')
    df['product_category_name'] = df['product_category_name_english']
    df.drop('product_category_name_english', axis=1, inplace=True)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Tambahan kolom waktu untuk analisis
    df['year'] = df['order_purchase_timestamp'].dt.year
    df['month'] = df['order_purchase_timestamp'].dt.month
    df['month_name'] = df['order_purchase_timestamp'].dt.month_name()
    df['day'] = df['order_purchase_timestamp'].dt.day
    df['day_of_week'] = df['order_purchase_timestamp'].dt.dayofweek
    df['day_name'] = df['order_purchase_timestamp'].dt.day_name()
    df['hour_of_day'] = df['order_purchase_timestamp'].dt.hour
    
    return df

try:
    # Load data
    df = load_data()
    
    # Sidebar Filters
    st.sidebar.header("Pilih Rentang Waktu analisis")
    
    # Filter tahun
    years = sorted(df['year'].unique())
    selected_years = st.sidebar.multiselect("Pilih Tahun", years, default=years)
    
    # Filter hanya jika user memilih setidaknya satu tahun
    if selected_years:
        df_filtered = df[df['year'].isin(selected_years)]
        
        # Filter berdasarkan rentang tanggal
        min_date = df_filtered['order_purchase_timestamp'].min().date()
        max_date = df_filtered['order_purchase_timestamp'].max().date()
        
        date_range = st.sidebar.date_input(
            "Pilih Rentang Tanggal",
            [min_date, min_date + timedelta(days=30)],
            min_value=min_date,
            max_value=max_date
        )
        
        # Memastikan rentang tanggal valid
        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered['order_purchase_timestamp'].dt.date >= start_date) & 
                (df_filtered['order_purchase_timestamp'].dt.date <= end_date)
            ]
            
            # Filter berdasarkan hari dalam seminggu
            days_map = {
                0: 'Senin', 
                1: 'Selasa', 
                2: 'Rabu', 
                3: 'Kamis', 
                4: 'Jumat', 
                5: 'Sabtu', 
                6: 'Minggu'
            }
            
            days_options = list(days_map.values())
            selected_days = st.sidebar.multiselect("Pilih Hari", days_options, default=days_options)
            
            # Mengonversi nama hari ke indeks untuk filter
            day_indices = [list(days_map.keys())[list(days_map.values()).index(day)] for day in selected_days]
            
            if day_indices:  # Hanya filter jika ada hari yang dipilih
                df_filtered = df_filtered[df_filtered['day_of_week'].isin(day_indices)]
            
            # Tampilkan KPI Metrics dalam 4 kolom
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_orders = df_filtered['order_id'].nunique()
                st.metric("Total Pesanan", f"{total_orders:,}")
            with col2:
                total_products = df_filtered['product_id'].nunique()
                st.metric("Total Produk Terjual", f"{total_products:,}")
            with col3:
                avg_price = df_filtered['price'].mean()
                st.metric("Rata-rata Harga", f"R$ {avg_price:.2f}")
            with col4:
                total_revenue = df_filtered['price'].sum()
                st.metric("Total Pendapatan", f"R$ {total_revenue:,.2f}")
            
            # Buat tab untuk berbagai visualisasi
            tab1, tab2, tab3 = st.tabs(["Pola Waktu Belanja", "Analisis Hari", "Tren Bulanan"])
            
            with tab1:
                st.subheader("Frekuensi Pembelian dalam Sehari")
                
                # Interaktivitas untuk rentang jam
                hour_min, hour_max = st.slider(
                    "Pilih Rentang Jam:",
                    0, 23, (0, 23)
                )
                
                hour_filtered = df_filtered[
                    (df_filtered['hour_of_day'] >= hour_min) & 
                    (df_filtered['hour_of_day'] <= hour_max)
                ]
                
                # Membuat visualisasi frekuensi per jam
                fig, ax = plt.subplots(figsize=(12, 6))
                
                hour_counts = hour_filtered['hour_of_day'].value_counts().sort_index()
                sns.barplot(x=hour_counts.index, y=hour_counts.values, ax=ax, palette='viridis')
                
                ax.set_xlabel("Jam dalam Sehari")
                ax.set_ylabel("Jumlah Pesanan")
                ax.set_title(f"Frekuensi Pembelian (Jam {hour_min}:00 - {hour_max}:00)")
                ax.set_xticks(range(hour_min, hour_max + 1))
                ax.set_xticklabels([f"{h}:00" for h in range(hour_min, hour_max + 1)])
                
                st.pyplot(fig)
                
                # Tampilkan tabel detail
                hour_detail = hour_filtered.groupby('hour_of_day').agg({
                    'order_id': pd.Series.nunique,
                    'price': 'sum'
                }).reset_index()
                
                hour_detail.columns = ['Jam', 'Jumlah Pesanan', 'Total Pendapatan (R$)']
                hour_detail['Jam'] = hour_detail['Jam'].apply(lambda x: f"{x}:00")
                st.dataframe(hour_detail, use_container_width=True)
            
            with tab2:
                st.subheader("Analisis Berdasarkan Hari dalam Seminggu")
                
                # Menambahkan nama hari dalam bahasa Indonesia
                df_filtered_day = df_filtered.copy()
                df_filtered_day['nama_hari'] = df_filtered_day['day_of_week'].map(days_map)
                
                # Buat 2 kolom untuk visualisasi hari
                col1, col2 = st.columns(2)
                
                with col1:
                    # Visualisasi jumlah pesanan per hari
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    day_order_counts = df_filtered_day.groupby('nama_hari')['order_id'].nunique().reindex(days_options)
                    
                    sns.barplot(
                        x=day_order_counts.index, 
                        y=day_order_counts.values, 
                        ax=ax,
                        palette='Blues_d'
                    )
                    
                    ax.set_xlabel("Hari")
                    ax.set_ylabel("Jumlah Pesanan")
                    ax.set_title("Jumlah Pesanan per Hari")
                    plt.xticks(rotation=45)
                    
                    st.pyplot(fig)
                
                with col2:
                    # Visualisasi pendapatan per hari
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    day_revenue = df_filtered_day.groupby('nama_hari')['price'].sum().reindex(days_options)
                    
                    sns.barplot(
                        x=day_revenue.index, 
                        y=day_revenue.values, 
                        ax=ax,
                        palette='Greens_d'
                    )
                    
                    ax.set_xlabel("Hari")
                    ax.set_ylabel("Total Pendapatan (R$)")
                    ax.set_title("Pendapatan per Hari")
                    plt.xticks(rotation=45)
                    
                    st.pyplot(fig)
                
                # Tampilkan tabel detail per hari
                day_stats = df_filtered_day.groupby('nama_hari').agg({
                    'order_id': pd.Series.nunique,
                    'price': 'sum',
                    'product_id': pd.Series.nunique
                }).reset_index()
                
                day_stats.columns = ['Hari', 'Jumlah Pesanan', 'Total Pendapatan (R$)', 'Jumlah Produk']
                # Mengurutkan berdasarkan urutan hari dalam seminggu
                day_order = {day: i for i, day in enumerate(days_options)}
                day_stats['sort_order'] = day_stats['Hari'].map(day_order)
                day_stats = day_stats.sort_values('sort_order').drop('sort_order', axis=1)
                
                st.dataframe(day_stats, use_container_width=True)
            
            with tab3:
                st.subheader("Tren Pembelian Bulanan")
                
                # Persiapkan data bulanan
                df_filtered['year_month'] = df_filtered['order_purchase_timestamp'].dt.strftime('%Y-%m')
                df_filtered['month_year_label'] = df_filtered['order_purchase_timestamp'].dt.strftime('%b %Y')
                
                monthly_data = df_filtered.groupby(['year_month', 'month_year_label']).agg({
                    'order_id': pd.Series.nunique,
                    'price': 'sum'
                }).reset_index()
                
                # Urutkan berdasarkan tahun-bulan
                monthly_data['sort_key'] = pd.to_datetime(monthly_data['year_month'] + '-01')
                monthly_data = monthly_data.sort_values('sort_key')
                
                # Visualisasi tren bulanan
                fig, ax1 = plt.subplots(figsize=(14, 7))
                
                # Plot jumlah pesanan
                ax1.set_xlabel('Bulan-Tahun')
                ax1.set_ylabel('Jumlah Pesanan', color='tab:blue')
                ax1.plot(monthly_data['month_year_label'], monthly_data['order_id'], 'o-', color='tab:blue', label='Pesanan')
                ax1.tick_params(axis='y', labelcolor='tab:blue')
                
                # Plot pendapatan pada axis kedua
                ax2 = ax1.twinx()
                ax2.set_ylabel('Total Pendapatan (R$)', color='tab:green')
                ax2.plot(monthly_data['month_year_label'], monthly_data['price'], 'o-', color='tab:green', label='Pendapatan')
                ax2.tick_params(axis='y', labelcolor='tab:green')
                
                # Judul dan legenda
                plt.title('Tren Pesanan dan Pendapatan per Bulan')
                plt.xticks(rotation=45)
                
                # Gabungkan legends dari kedua axes
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
                
                fig.tight_layout()
                st.pyplot(fig)
                
                # Visualisasi heatmap pola belanja
                st.subheader("Pola Belanja Berdasarkan Hari dan Jam")
                
                # Membuat data untuk heatmap
                heatmap_data = df_filtered.groupby(['day_of_week', 'hour_of_day']).size().reset_index(name='count')
                heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour_of_day', values='count').fillna(0)
                
                # Mengubah indeks angka menjadi nama hari
                heatmap_pivot.index = [days_map[day] for day in heatmap_pivot.index]
                
                # Membuat heatmap
                fig, ax = plt.subplots(figsize=(14, 8))
                sns.heatmap(
                    heatmap_pivot, 
                    annot=False, 
                    cmap="viridis", 
                    ax=ax,
                    cbar_kws={'label': 'Jumlah Pesanan'}
                )
                
                ax.set_xlabel("Jam")
                ax.set_ylabel("Hari")
                ax.set_title("Heatmap Pesanan Berdasarkan Hari dan Jam")
                
                st.pyplot(fig)
        
        else:
            st.warning("Silakan pilih rentang tanggal (dari dan sampai)")
    else:
        st.warning("Silakan pilih minimal satu tahun")

except Exception as e:
    st.error(f"Error: {e}")
    st.error("Pastikan file data tersedia di folder 'E-Commerce Public Dataset'")

# Footer
st.markdown("---")
st.caption("© 2025 Dashboard E-Commerce Olist Store Brazil")
