import json
from typing import Dict, Any, List
from enum import Enum, auto


class CICDStage(Enum):
    """Enumeration of CI/CD pipeline stages"""

    BUILD = auto()
    TEST = auto()
    ANALYZE = auto()
    DEPLOY = auto()


class DMAICCICDIntegration:
    """Integrates DMAIC methodology with CI/CD pipelines"""

    def __init__(self, dmaic_handler, output_handler):
        """Initialize with DMAIC handler and output handler"""
        self.dmaic_handler = dmaic_handler
        self.output_handler = output_handler

    def map_stage_to_phase(self, stage: CICDStage) -> str:
        """Map CI/CD stage to DMAIC phase for analysis"""
        mapping = {
            CICDStage.BUILD: "DEFINE",
            CICDStage.TEST: "MEASURE",
            CICDStage.ANALYZE: "ANALYZE",
            CICDStage.DEPLOY: "IMPROVE",
        }
        return mapping.get(stage, "CONTROL")

    def process_pipeline_results(
        self, stage: CICDStage, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process CI/CD pipeline results using DMAIC methodology"""
        dmaic_phase = self.map_stage_to_phase(stage)

        # Format the results for DMAIC analysis
        prompt = f"Analyze the following {stage.name} stage results using {dmaic_phase} principles:\n"
        prompt += json.dumps(results, indent=2)

        # Get DMAIC insights
        response = self.dmaic_handler.interact(prompt)

        # Log the interaction
        self.output_handler.log_interaction(prompt, response)

        return {
            "stage": stage.name,
            "dmaic_phase": dmaic_phase,
            "raw_results": results,
            "dmaic_insights": response,
            "recommendations": self._extract_recommendations(response),
        }

    def _extract_recommendations(self, dmaic_response: str) -> List[str]:
        """Extract actionable recommendations from DMAIC response"""
        # Simple extraction - in a real implementation, use more sophisticated NLP
        recommendations = []
        for line in dmaic_response.split("\n"):
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "suggest", "should", "improve"]
            ):
                recommendations.append(line.strip())
        return recommendations

    def generate_report(
        self, all_stage_results: Dict[str, Any], output_path: str
    ) -> str:
        """Generate a comprehensive CI/CD pipeline report with DMAIC insights"""
        report = {
            "summary": "DMAIC Analysis of CI/CD Pipeline Results",
            "stages": all_stage_results,
            "overall_recommendations": [],
        }

        # Consolidate recommendations
        for stage, results in all_stage_results.items():
            if "recommendations" in results:
                for rec in results["recommendations"]:
                    report["overall_recommendations"].append(f"[{stage}] {rec}")

        # Save report
        return self.output_handler.save_results(report, output_path)
