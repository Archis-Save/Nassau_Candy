import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Nassau Candy Route Efficiency", layout="wide")
st.title("Factory-to-Customer Shipping Route Efficiency")
st.caption("Nassau Candy Distributor — route-level operational analytics")

@st.cache_data
def load_data():
    df=pd.read_csv("Nassau_Candy_Route_Cleaned.csv")
    df["Order Date"]=pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"]=pd.to_datetime(df["Ship Date"], errors="coerce")
    df["LeadTime"]=(df["Ship Date"]-df["Order Date"]).dt.days
    return df
df=load_data()

with st.sidebar:
    st.header("Filters")
    min_date,max_date=df["Order Date"].min().date(),df["Order Date"].max().date()
    dates=st.date_input("Order date range",(min_date,max_date),min_value=min_date,max_value=max_date)
    regions=st.multiselect("Region",sorted(df.Region.dropna().unique()),default=sorted(df.Region.dropna().unique()))
    states=st.multiselect("State",sorted(df["State/Province"].dropna().unique()))
    modes=st.multiselect("Ship mode",sorted(df["Ship Mode"].dropna().unique()),default=sorted(df["Ship Mode"].dropna().unique()))
    threshold=st.slider("Delay threshold (days)",1,30,7)

if len(dates)==2:
    f=df[df["Order Date"].dt.date.between(dates[0],dates[1])]
else: f=df.copy()
f=f[f.Region.isin(regions) & f["Ship Mode"].isin(modes)]
if states: f=f[f["State/Province"].isin(states)]

c1,c2,c3,c4=st.columns(4)
c1.metric("Shipments",f"{len(f):,}")
c2.metric("Orders",f"{f['Order ID'].nunique():,}")
c3.metric("Avg lead time",f"{f.LeadTime.mean():.1f} days")
c4.metric("Delay frequency",f"{(f.LeadTime>threshold).mean()*100:.1f}%")

tab1,tab2,tab3,tab4=st.tabs(["Overview","Route Efficiency","Geography","Ship Modes"])

with tab1:
    st.subheader("Route efficiency overview")
    route=f.groupby(["Factory","State/Province"]).agg(Shipments=("Order ID","size"),AverageLeadTime=("LeadTime","mean"),LeadTimeStd=("LeadTime","std")).reset_index()
    route["EfficiencyScore"]=100*(route.AverageLeadTime.max()-route.AverageLeadTime)/(route.AverageLeadTime.max()-route.AverageLeadTime.min()) if len(route)>1 and route.AverageLeadTime.max()!=route.AverageLeadTime.min() else 100
    col1,col2=st.columns(2)
    with col1:
        fig=px.bar(route.sort_values("AverageLeadTime").head(15),x="AverageLeadTime",y="State/Province",color="Factory",orientation="h",title="Fastest factory-state routes")
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        fig=px.bar(route.sort_values("AverageLeadTime",ascending=False).head(15),x="AverageLeadTime",y="State/Province",color="Factory",orientation="h",title="Slowest factory-state routes")
        st.plotly_chart(fig,use_container_width=True)
    st.dataframe(route.sort_values("AverageLeadTime"),use_container_width=True)

with tab2:
    st.subheader("Route drill-down")
    factory=st.selectbox("Factory",sorted(f.Factory.dropna().unique()))
    r=f[f.Factory==factory].groupby(["State/Province","Region"]).agg(Shipments=("Order ID","size"),AverageLeadTime=("LeadTime","mean"),MedianLeadTime=("LeadTime","median"),StdLeadTime=("LeadTime","std")).reset_index()
    st.dataframe(r.sort_values("AverageLeadTime"),use_container_width=True)
    state=st.selectbox("State drill-down",sorted(f[f.Factory==factory]["State/Province"].unique()))
    orders=f[(f.Factory==factory)&(f["State/Province"]==state)].sort_values("Order Date")
    st.dataframe(orders[["Order ID","Order Date","Ship Date","Ship Mode","Product Name","LeadTime"]],use_container_width=True)

with tab3:
    st.subheader("Geographic bottlenecks")
    geo=f.groupby("Region").agg(Shipments=("Order ID","size"),AverageLeadTime=("LeadTime","mean"),DelayFrequency=("LeadTime",lambda x:(x>threshold).mean()*100)).reset_index()
    st.dataframe(geo.sort_values("AverageLeadTime",ascending=False),use_container_width=True)
    fig=px.scatter(geo,x="Shipments",y="AverageLeadTime",size="DelayFrequency",text="Region",title="Shipment volume vs average lead time")
    st.plotly_chart(fig,use_container_width=True)
    state=f.groupby("State/Province").agg(Shipments=("Order ID","size"),AverageLeadTime=("LeadTime","mean")).reset_index()
    fig=px.bar(state.sort_values("AverageLeadTime",ascending=False).head(20),x="AverageLeadTime",y="State/Province",orientation="h",title="States with highest average lead time")
    st.plotly_chart(fig,use_container_width=True)

with tab4:
    st.subheader("Ship mode comparison")
    mode=f.groupby("Ship Mode").agg(Shipments=("Order ID","size"),AverageLeadTime=("LeadTime","mean"),MedianLeadTime=("LeadTime","median"),DelayFrequency=("LeadTime",lambda x:(x>threshold).mean()*100)).reset_index()
    st.dataframe(mode,use_container_width=True)
    fig=px.bar(mode,x="Ship Mode",y="AverageLeadTime",text_auto=".1f",title="Average lead time by ship mode")
    st.plotly_chart(fig,use_container_width=True)
    fig=px.box(f,x="Ship Mode",y="LeadTime",title="Lead-time distribution by ship mode")
    st.plotly_chart(fig,use_container_width=True)

st.warning("Data-quality note: supplied Order Date → Ship Date gaps are unusually large (904–1,642 days). Validate the source dates before using these metrics for operational SLA decisions.")
