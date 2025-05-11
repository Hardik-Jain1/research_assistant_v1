# app/core/summarizer_service.py
from flask import current_app
# Assuming summarizer.llm_summarizer and its adapted functions are accessible
from summarizer.llm_summarizer import (
    summarize_arxiv_papers as summarize_arxiv_papers_external,
    synthesize_insights_from_summaries as synthesize_insights_external
)
from app.services.litellm_service import completion as litellm_completion_wrapper

class SummarizerService:
    @staticmethod
    def generate_individual_summaries(arxiv_results: list[dict]) -> list[dict]:
        """
        Generates individual summaries for a list of arXiv results.
        arxiv_results: List of dicts from ArxivService, each should have 'title', 'abstract', 'paper_id'.
        """
        try:
            # Pass the app config and the LiteLLM completion wrapper
            summaries = summarize_arxiv_papers_external(
                arxiv_results=arxiv_results,
                config=current_app.config,
                llm_completion_func=litellm_completion_wrapper,
                # max_tokens_per_summary can be picked from current_app.config if needed
            )
            return summaries
        except Exception as e:
            current_app.logger.error(f"Error generating individual summaries: {e}")
            raise

    @staticmethod
    def generate_consolidated_summary(paper_summaries: list[dict], query: str) -> dict:
        """
        Generates a consolidated summary from individual paper summaries.
        paper_summaries: List of dicts, each with 'paper_id', 'title', 'summary'.
        query: The original user research query.
        """
        try:
            # Pass the app config and the LiteLLM completion wrapper
            synthesized_insight = synthesize_insights_external(
                paper_summaries=paper_summaries,
                query=query,
                config=current_app.config,
                llm_completion_func=litellm_completion_wrapper,
                # max_tokens_synthesis can be picked from current_app.config if needed
            )
            return synthesized_insight # This is a dict with 'content' and token usage
        except Exception as e:
            current_app.logger.error(f"Error generating consolidated summary for query '{query}': {e}")
            raise