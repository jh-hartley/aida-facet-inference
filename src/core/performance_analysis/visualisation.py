import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.performance_analysis.analysis_models import (
    ExperimentAnalysis,
)


class PredictionVisualiser:
    """Visualiser for prediction analysis results."""

    def __init__(self, analysis: ExperimentAnalysis):
        self.analysis = analysis

    def plot_confidence_correlation(self) -> go.Figure:
        """Plot correlation between confidence and accuracy."""
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                line=dict(dash="dash", color="gray"),
                name="Perfect Correlation",
            )
        )

        for segment in self.analysis.confidence_segments:
            fig.add_trace(
                go.Scatter(
                    x=[segment.confidence_level.value],
                    y=[segment.metrics.accuracy],
                    mode="markers+text",
                    marker=dict(size=10),
                    text=[f"n={segment.sample_size}"],
                    textposition="top center",
                    name=segment.confidence_level.value,
                )
            )

        fig.update_layout(
            title="Confidence vs Accuracy by Segment",
            xaxis_title="Confidence Level",
            yaxis_title="Accuracy",
            showlegend=True,
        )
        return fig

    def plot_category_performance(self) -> go.Figure:
        """Plot performance metrics by category."""
        categories = [m.category_name for m in self.analysis.category_metrics]
        accuracies = [
            m.metrics.accuracy for m in self.analysis.category_metrics
        ]
        sample_sizes = [m.sample_size for m in self.analysis.category_metrics]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=categories,
                y=accuracies,
                text=[f"n={n}" for n in sample_sizes],
                textposition="auto",
                name="Accuracy",
            )
        )

        fig.update_layout(
            title="Prediction Accuracy by Category",
            xaxis_title="Category",
            yaxis_title="Accuracy",
            showlegend=False,
            xaxis_tickangle=-45,
        )
        return fig

    def plot_attribute_performance(self) -> go.Figure:
        """Plot performance metrics by attribute."""
        attributes = [
            m.attribute_name for m in self.analysis.attribute_metrics
        ]
        accuracies = [
            m.metrics.accuracy for m in self.analysis.attribute_metrics
        ]
        sample_sizes = [m.sample_size for m in self.analysis.attribute_metrics]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=attributes,
                y=accuracies,
                text=[f"n={n}" for n in sample_sizes],
                textposition="auto",
                name="Accuracy",
            )
        )

        fig.update_layout(
            title="Prediction Accuracy by Attribute",
            xaxis_title="Attribute",
            yaxis_title="Accuracy",
            showlegend=False,
            xaxis_tickangle=-45,
        )
        return fig

    def plot_gap_count_impact(self) -> go.Figure:
        """Plot impact of gap count on prediction performance."""
        gap_counts = [m.gap_count for m in self.analysis.gap_count_metrics]
        accuracies = [
            m.metrics.accuracy for m in self.analysis.gap_count_metrics
        ]
        sample_sizes = [m.sample_size for m in self.analysis.gap_count_metrics]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=gap_counts,
                y=accuracies,
                mode="markers+lines+text",
                text=[f"n={n}" for n in sample_sizes],
                textposition="top center",
                name="Accuracy",
            )
        )

        fig.update_layout(
            title="Impact of Gap Count on Prediction Accuracy",
            xaxis_title="Number of Gaps",
            yaxis_title="Accuracy",
            showlegend=False,
        )
        return fig

    def plot_description_length_impact(self) -> go.Figure:
        """Plot impact of description length on prediction performance."""
        segments = [
            m.length_segment for m in self.analysis.description_length_metrics
        ]
        accuracies = [
            m.metrics.accuracy
            for m in self.analysis.description_length_metrics
        ]
        sample_sizes = [
            m.sample_size for m in self.analysis.description_length_metrics
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=segments,
                y=accuracies,
                text=[f"n={n}" for n in sample_sizes],
                textposition="auto",
                name="Accuracy",
            )
        )

        fig.update_layout(
            title="Impact of Description Length on Prediction Accuracy",
            xaxis_title="Description Length",
            yaxis_title="Accuracy",
            showlegend=False,
        )
        return fig

    def plot_overall_metrics(self) -> go.Figure:
        """Plot overall performance metrics."""
        metrics = self.analysis.overall_metrics
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=["Accuracy", "F1 Score", "Precision", "Recall"],
                y=[
                    metrics.accuracy,
                    metrics.f1_score,
                    metrics.precision,
                    metrics.recall,
                ],
                text=[
                    f"{v:.2%}"
                    for v in [
                        metrics.accuracy,
                        metrics.f1_score,
                        metrics.precision,
                        metrics.recall,
                    ]
                ],
                textposition="auto",
            )
        )

        fig.update_layout(
            title="Overall Prediction Performance",
            yaxis_title="Score",
            showlegend=False,
            yaxis_tickformat=".0%",
        )
        return fig

    def plot_confidence_analysis(self) -> go.Figure:
        """
        Plot detailed confidence analysis with correct vs
        incorrect predictions.
        """
        fig = go.Figure()

        # Sort confidence segments by level
        segments = sorted(
            self.analysis.confidence_segments,
            key=lambda x: x.confidence_level.value,
        )

        # Calculate correct and incorrect predictions
        correct = [s.metrics.correct_predictions for s in segments]
        incorrect = [
            s.metrics.total_predictions - s.metrics.correct_predictions
            for s in segments
        ]

        # Add stacked bars
        fig.add_trace(
            go.Bar(
                x=[s.confidence_level.value for s in segments],
                y=correct,
                name="Correct",
                marker_color="green",
            )
        )

        fig.add_trace(
            go.Bar(
                x=[s.confidence_level.value for s in segments],
                y=incorrect,
                name="Incorrect",
                marker_color="red",
            )
        )

        # Add expected accuracy line
        expected_accuracy = [s.confidence_level.value for s in segments]
        fig.add_trace(
            go.Scatter(
                x=[s.confidence_level.value for s in segments],
                y=expected_accuracy,
                mode="lines",
                name="Expected Accuracy",
                line=dict(dash="dash", color="gray"),
            )
        )

        fig.update_layout(
            title="Confidence Analysis",
            xaxis_title="Confidence Level",
            yaxis_title="Number of Predictions",
            barmode="stack",
            showlegend=True,
        )
        return fig

    def plot_category_heatmap(self) -> go.Figure:
        """Plot category performance as a heatmap."""
        # Sort categories by accuracy
        categories = sorted(
            self.analysis.category_metrics,
            key=lambda x: x.metrics.accuracy,
            reverse=True,
        )

        # Prepare data
        category_names = [m.category_name for m in categories]
        accuracies = [m.metrics.accuracy for m in categories]
        sample_sizes = [m.sample_size for m in categories]

        # Create heatmap
        fig = go.Figure(
            go.Heatmap(
                z=[accuracies],
                x=category_names,
                y=["Accuracy"],
                colorscale="RdYlGn",
                text=[
                    [
                        f"{acc:.1%}\nn={n}"
                        for acc, n in zip(accuracies, sample_sizes)
                    ]
                ],
                texttemplate="%{text}",
                textfont={"size": 10},
            )
        )

        fig.update_layout(
            title="Category Performance Heatmap",
            xaxis_title="Category",
            yaxis_title="",
            height=200,
            xaxis_tickangle=-45,
        )
        return fig

    def plot_attribute_heatmap(self) -> go.Figure:
        """Plot attribute performance as a heatmap."""
        # Sort attributes by accuracy
        attributes = sorted(
            self.analysis.attribute_metrics,
            key=lambda x: x.metrics.accuracy,
            reverse=True,
        )

        # Prepare data
        attribute_names = [m.attribute_name for m in attributes]
        accuracies = [m.metrics.accuracy for m in attributes]
        sample_sizes = [m.sample_size for m in attributes]

        # Create heatmap
        fig = go.Figure(
            go.Heatmap(
                z=[accuracies],
                x=attribute_names,
                y=["Accuracy"],
                colorscale="RdYlGn",
                text=[
                    [
                        f"{acc:.1%}\nn={n}"
                        for acc, n in zip(accuracies, sample_sizes)
                    ]
                ],
                texttemplate="%{text}",
                textfont={"size": 10},
            )
        )

        fig.update_layout(
            title="Attribute Performance Heatmap",
            xaxis_title="Attribute",
            yaxis_title="",
            height=200,
            xaxis_tickangle=-45,
        )
        return fig

    def plot_aggregated_confusion(self) -> go.Figure:
        """Plot aggregated confusion matrix for all predictions."""
        # Calculate aggregated confusion matrix
        total_correct = sum(
            m.metrics.correct_predictions
            for m in self.analysis.attribute_metrics
        )
        total_incorrect = sum(
            m.metrics.total_predictions - m.metrics.correct_predictions
            for m in self.analysis.attribute_metrics
        )

        # Create confusion matrix
        confusion = np.array(
            [
                [total_correct, total_incorrect],
                [total_incorrect, total_correct],
            ]
        )

        fig = go.Figure(
            go.Heatmap(
                z=confusion,
                x=["Predicted Correct", "Predicted Incorrect"],
                y=["Actual Correct", "Actual Incorrect"],
                colorscale="RdYlGn",
                text=confusion,
                texttemplate="%{text}",
                textfont={"size": 12},
            )
        )

        fig.update_layout(
            title="Aggregated Confusion Matrix",
            xaxis_title="Predicted",
            yaxis_title="Actual",
        )
        return fig

    def create_improved_dashboard(self) -> go.Figure:
        """Create an improved dashboard with new visualizations."""
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "Overall Metrics",
                "Confidence Analysis",
                "Category Performance",
                "Attribute Performance",
                "Gap Count Impact",
                "Aggregated Confusion",
            ),
        )

        # Add overall metrics
        overall = self.plot_overall_metrics()
        for trace in overall.data:
            fig.add_trace(trace, row=1, col=1)

        # Add confidence analysis
        confidence = self.plot_confidence_analysis()
        for trace in confidence.data:
            fig.add_trace(trace, row=1, col=2)

        # Add category heatmap
        category = self.plot_category_heatmap()
        for trace in category.data:
            fig.add_trace(trace, row=2, col=1)

        # Add attribute heatmap
        attribute = self.plot_attribute_heatmap()
        for trace in attribute.data:
            fig.add_trace(trace, row=2, col=2)

        # Add gap count impact
        gap_count = self.plot_gap_count_impact()
        for trace in gap_count.data:
            fig.add_trace(trace, row=3, col=1)

        # Add aggregated confusion matrix
        confusion = self.plot_aggregated_confusion()
        for trace in confusion.data:
            fig.add_trace(trace, row=3, col=2)

        fig.update_layout(
            height=1200,
            width=1600,
            title_text=(
                f"Prediction Analysis Dashboard - "
                f"Experiment {self.analysis.experiment_key}"
            ),
            showlegend=True,
        )

        return fig
