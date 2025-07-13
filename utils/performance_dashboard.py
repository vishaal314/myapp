"""
Performance Dashboard for DataGuardian Pro
Real-time monitoring and optimization insights
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, List
import logging

from utils.database_optimizer import get_optimized_db
from utils.redis_cache import get_cache, get_performance_cache
from utils.session_optimizer import get_session_optimizer
from utils.code_profiler import get_profiler

logger = logging.getLogger(__name__)

class PerformanceDashboard:
    """Performance monitoring dashboard"""
    
    def __init__(self):
        self.db_optimizer = get_optimized_db()
        self.redis_cache = get_cache()
        self.performance_cache = get_performance_cache()
        self.session_optimizer = get_session_optimizer()
        self.profiler = get_profiler()
    
    def render_dashboard(self):
        """Render the complete performance dashboard"""
        st.header("🚀 Performance Dashboard")
        
        # Performance summary cards
        self._render_summary_cards()
        
        # System metrics
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_system_metrics()
            self._render_database_performance()
        
        with col2:
            self._render_cache_performance()
            self._render_session_metrics()
        
        # Detailed analysis
        st.subheader("📊 Detailed Analysis")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Function Performance", "Query Analysis", "Bottlenecks", "Recommendations"])
        
        with tab1:
            self._render_function_performance()
        
        with tab2:
            self._render_query_analysis()
        
        with tab3:
            self._render_bottleneck_analysis()
        
        with tab4:
            self._render_recommendations()
    
    def _render_summary_cards(self):
        """Render performance summary cards"""
        try:
            # Get performance data
            db_stats = self.db_optimizer.get_performance_stats()
            cache_stats = self.redis_cache.get_stats()
            session_stats = self.session_optimizer.get_session_stats()
            profiler_report = self.profiler.get_performance_report()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Database Performance",
                    f"{db_stats['pool_stats']['avg_query_time']:.3f}s",
                    f"{db_stats['pool_stats']['total_queries']} queries"
                )
            
            with col2:
                hit_rate = cache_stats.get('hit_rate', 0) * 100
                st.metric(
                    "Cache Hit Rate",
                    f"{hit_rate:.1f}%",
                    f"{cache_stats.get('total_keys', 0)} keys"
                )
            
            with col3:
                st.metric(
                    "Active Sessions",
                    session_stats['active_sessions'],
                    f"Peak: {session_stats['peak_concurrent']}"
                )
            
            with col4:
                memory_percent = session_stats.get('system_resources', {}).get('memory_percent', 0)
                st.metric(
                    "Memory Usage",
                    f"{memory_percent:.1f}%",
                    f"CPU: {session_stats.get('system_resources', {}).get('cpu_percent', 0):.1f}%"
                )
                
        except Exception as e:
            st.error(f"Error rendering summary cards: {e}")
    
    def _render_system_metrics(self):
        """Render system performance metrics"""
        st.subheader("💻 System Metrics")
        
        try:
            session_stats = self.session_optimizer.get_session_stats()
            system_resources = session_stats.get('system_resources', {})
            
            # Memory usage gauge
            fig_memory = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = system_resources.get('memory_percent', 0),
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Memory Usage (%)"},
                delta = {'reference': 70},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_memory.update_layout(height=300)
            st.plotly_chart(fig_memory, use_container_width=True)
            
            # CPU usage gauge
            fig_cpu = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = system_resources.get('cpu_percent', 0),
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "CPU Usage (%)"},
                delta = {'reference': 70},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_cpu.update_layout(height=300)
            st.plotly_chart(fig_cpu, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering system metrics: {e}")
    
    def _render_database_performance(self):
        """Render database performance metrics"""
        st.subheader("🗄️ Database Performance")
        
        try:
            db_stats = self.db_optimizer.get_performance_stats()
            pool_stats = db_stats['pool_stats']
            
            # Database metrics
            metrics_data = {
                'Metric': ['Total Queries', 'Slow Queries', 'Cache Hits', 'Cache Misses', 'Avg Query Time'],
                'Value': [
                    pool_stats['total_queries'],
                    pool_stats['slow_queries'],
                    pool_stats['cache_hits'],
                    pool_stats['cache_misses'],
                    f"{pool_stats['avg_query_time']:.3f}s"
                ]
            }
            
            df_metrics = pd.DataFrame(metrics_data)
            st.dataframe(df_metrics, use_container_width=True)
            
            # Query performance chart
            if db_stats.get('top_queries'):
                query_data = []
                for query in db_stats['top_queries'][:5]:
                    query_data.append({
                        'Query': query['query'][:50] + '...' if len(query['query']) > 50 else query['query'],
                        'Total Time': query['total_time'],
                        'Calls': query['calls'],
                        'Mean Time': query['mean_time']
                    })
                
                if query_data:
                    df_queries = pd.DataFrame(query_data)
                    fig_queries = px.bar(df_queries, x='Query', y='Total Time', 
                                       title="Top Queries by Total Time")
                    fig_queries.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_queries, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering database performance: {e}")
    
    def _render_cache_performance(self):
        """Render cache performance metrics"""
        st.subheader("⚡ Cache Performance")
        
        try:
            cache_stats = self.redis_cache.get_stats()
            
            # Cache hit rate donut chart
            hit_rate = cache_stats.get('hit_rate', 0) * 100
            miss_rate = 100 - hit_rate
            
            fig_cache = go.Figure(data=[go.Pie(
                labels=['Cache Hits', 'Cache Misses'],
                values=[hit_rate, miss_rate],
                hole=.3
            )])
            fig_cache.update_layout(
                title="Cache Hit Rate",
                annotations=[dict(text=f'{hit_rate:.1f}%', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig_cache, use_container_width=True)
            
            # Cache statistics
            cache_metrics = {
                'Connected': '✅' if cache_stats.get('connected', False) else '❌',
                'Total Keys': cache_stats.get('total_keys', 0),
                'Memory Used': cache_stats.get('memory_used', 'N/A'),
                'Hits': cache_stats.get('hits', 0),
                'Misses': cache_stats.get('misses', 0),
                'Errors': cache_stats.get('errors', 0)
            }
            
            for key, value in cache_metrics.items():
                st.metric(key, value)
                
        except Exception as e:
            st.error(f"Error rendering cache performance: {e}")
    
    def _render_session_metrics(self):
        """Render session performance metrics"""
        st.subheader("👥 Session Metrics")
        
        try:
            session_stats = self.session_optimizer.get_session_stats()
            
            # Session overview
            st.metric("Total Sessions", session_stats['total_sessions'])
            st.metric("Active Sessions", session_stats['active_sessions'])
            st.metric("Expired Sessions", session_stats['expired_sessions'])
            st.metric("Concurrent Users", session_stats['concurrent_users'])
            st.metric("Peak Concurrent", session_stats['peak_concurrent'])
            
            # Session duration chart
            avg_duration = session_stats.get('session_duration_avg', 0) / 60  # Convert to minutes
            st.metric("Avg Session Duration", f"{avg_duration:.1f} min")
            
            # Memory usage by sessions
            memory_usage = session_stats.get('memory_usage', {})
            if memory_usage:
                st.metric("Session Memory (RSS)", f"{memory_usage.get('rss_mb', 0):.1f} MB")
                st.metric("Session Memory (VMS)", f"{memory_usage.get('vms_mb', 0):.1f} MB")
                st.metric("Memory Percent", f"{memory_usage.get('percent', 0):.1f}%")
                
        except Exception as e:
            st.error(f"Error rendering session metrics: {e}")
    
    def _render_function_performance(self):
        """Render function performance analysis"""
        try:
            profiler_report = self.profiler.get_performance_report()
            slow_functions = profiler_report['top_slow_functions']
            
            if slow_functions:
                # Convert to DataFrame for better display
                df_functions = pd.DataFrame(slow_functions)
                
                # Performance chart
                fig_perf = px.bar(df_functions, x='name', y='avg_time', 
                                title="Slowest Functions by Average Time")
                fig_perf.update_xaxes(tickangle=45)
                st.plotly_chart(fig_perf, use_container_width=True)
                
                # Detailed table
                st.dataframe(df_functions, use_container_width=True)
            else:
                st.info("No function performance data available yet")
                
        except Exception as e:
            st.error(f"Error rendering function performance: {e}")
    
    def _render_query_analysis(self):
        """Render database query analysis"""
        try:
            profiler_report = self.profiler.get_performance_report()
            slow_queries = profiler_report['slow_queries']
            
            if slow_queries:
                st.subheader("🐌 Slow Queries")
                
                for i, query in enumerate(slow_queries, 1):
                    with st.expander(f"Query {i} - {query['execution_time']:.3f}s"):
                        st.code(query['query'], language='sql')
                        st.write(f"**Execution Time:** {query['execution_time']:.3f}s")
                        st.write(f"**Function:** {query['function']}")
                        st.write(f"**Timestamp:** {query['timestamp']}")
                        if query.get('params'):
                            st.write(f"**Parameters:** {query['params']}")
            else:
                st.info("No slow queries detected")
                
        except Exception as e:
            st.error(f"Error rendering query analysis: {e}")
    
    def _render_bottleneck_analysis(self):
        """Render bottleneck analysis"""
        try:
            profiler_report = self.profiler.get_performance_report()
            bottlenecks = profiler_report['bottlenecks']
            
            if bottlenecks:
                st.subheader("🔴 Performance Bottlenecks")
                
                # Convert to DataFrame
                df_bottlenecks = pd.DataFrame(bottlenecks)
                
                # Bottleneck chart
                fig_bottlenecks = px.scatter(df_bottlenecks, x='occurrences', y='avg_time',
                                           size='avg_time', color='function',
                                           title="Bottlenecks: Frequency vs Average Time")
                st.plotly_chart(fig_bottlenecks, use_container_width=True)
                
                # Detailed table
                st.dataframe(df_bottlenecks, use_container_width=True)
            else:
                st.success("No performance bottlenecks detected")
                
        except Exception as e:
            st.error(f"Error rendering bottleneck analysis: {e}")
    
    def _render_recommendations(self):
        """Render optimization recommendations"""
        try:
            suggestions = self.profiler.get_optimization_suggestions()
            profiler_report = self.profiler.get_performance_report()
            recommendations = profiler_report['recommendations']
            
            if suggestions or recommendations:
                st.subheader("💡 Optimization Recommendations")
                
                # Priority-based recommendations
                high_priority = [s for s in suggestions if s.get('priority') == 'high']
                medium_priority = [s for s in suggestions if s.get('priority') == 'medium']
                
                if high_priority:
                    st.error("🚨 High Priority Issues")
                    for rec in high_priority:
                        st.write(f"**{rec['type'].replace('_', ' ').title()}:** {rec['issue']}")
                        st.write(f"💡 {rec['suggestion']}")
                        st.write("---")
                
                if medium_priority:
                    st.warning("⚠️ Medium Priority Issues")
                    for rec in medium_priority:
                        st.write(f"**{rec['type'].replace('_', ' ').title()}:** {rec['issue']}")
                        st.write(f"💡 {rec['suggestion']}")
                        st.write("---")
                
                # Recent recommendations
                if recommendations:
                    st.info("📋 Recent Recommendations")
                    for rec in recommendations[-5:]:  # Last 5 recommendations
                        st.write(f"**{rec['category'].replace('_', ' ').title()}:** {rec['issue']}")
                        st.write(f"💡 {rec['suggestion']}")
                        st.write(f"🕒 {rec['timestamp']}")
                        st.write("---")
            else:
                st.success("🎉 No optimization recommendations at this time!")
                
        except Exception as e:
            st.error(f"Error rendering recommendations: {e}")

def render_performance_dashboard():
    """Render the performance dashboard"""
    dashboard = PerformanceDashboard()
    dashboard.render_dashboard()