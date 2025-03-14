#!/bin/bash

# Remove all output

rm_check() {
    [ -e $1 ] && rm -r $1
}

rm_check plots/basic/cats_arbitrary
rm_check plots/basic/cats_path
rm_check plots/basic/cats_reg
rm_check plots/basic/qv
rm_check plots/basic/PriceDegreeBox_caption.tex
rm_check plots/basic/PriceDegreeBox.eps
rm_check plots/basic/PriceDegreeBox.pdf
rm_check plots/basic/PriceTermsBox_caption.tex
rm_check plots/basic/PriceTermsBox.eps
rm_check plots/basic/PriceTermsBox.pdf
rm_check plots/basic/PriceTermsPersonalizedBox_caption.tex
rm_check plots/basic/PriceTermsPersonalizedBox.eps
rm_check plots/basic/PriceTermsPersonalizedBox.pdf

rm_check plots/XorPrices

rm_check tables/basic/Basic_cats_arbitrary_10_full_doc.pdf
rm_check tables/basic/Basic_cats_arbitrary_10_full.tex
rm_check tables/basic/Basic_cats_arbitrary_10_full.tex.md5
rm_check tables/basic/Basic_cats_arbitrary_10_partial_doc.pdf
rm_check tables/basic/Basic_cats_arbitrary_10_partial.tex
rm_check tables/basic/Basic_cats_arbitrary_10_partial.tex.md5
rm_check tables/basic/Basic_cats_arbitrary_30_full_doc.pdf
rm_check tables/basic/Basic_cats_arbitrary_30_full.tex
rm_check tables/basic/Basic_cats_arbitrary_30_full.tex.md5
rm_check tables/basic/Basic_cats_arbitrary_30_partial_doc.pdf
rm_check tables/basic/Basic_cats_arbitrary_30_partial.tex
rm_check tables/basic/Basic_cats_arbitrary_30_partial.tex.md5
rm_check tables/basic/Basic_cats_path_10_full_doc.pdf
rm_check tables/basic/Basic_cats_path_10_full.tex
rm_check tables/basic/Basic_cats_path_10_full.tex.md5
rm_check tables/basic/Basic_cats_path_10_partial_doc.pdf
rm_check tables/basic/Basic_cats_path_10_partial.tex
rm_check tables/basic/Basic_cats_path_10_partial.tex.md5
rm_check tables/basic/Basic_cats_path_30_full_doc.pdf
rm_check tables/basic/Basic_cats_path_30_full.tex
rm_check tables/basic/Basic_cats_path_30_full.tex.md5
rm_check tables/basic/Basic_cats_path_30_partial_doc.pdf
rm_check tables/basic/Basic_cats_path_30_partial.tex
rm_check tables/basic/Basic_cats_path_30_partial.tex.md5
rm_check tables/basic/Basic_cats_reg_10_full_doc.pdf
rm_check tables/basic/Basic_cats_reg_10_full.tex
rm_check tables/basic/Basic_cats_reg_10_full.tex.md5
rm_check tables/basic/Basic_cats_reg_10_partial_doc.pdf
rm_check tables/basic/Basic_cats_reg_10_partial.tex
rm_check tables/basic/Basic_cats_reg_10_partial.tex.md5
rm_check tables/basic/Basic_cats_reg_30_full_doc.pdf
rm_check tables/basic/Basic_cats_reg_30_full.tex
rm_check tables/basic/Basic_cats_reg_30_full.tex.md5
rm_check tables/basic/Basic_cats_reg_30_partial_doc.pdf
rm_check tables/basic/Basic_cats_reg_30_partial.tex
rm_check tables/basic/Basic_cats_reg_30_partial.tex.md5
rm_check tables/basic/Basic_qv_10_full_doc.pdf
rm_check tables/basic/Basic_qv_10_full.tex
rm_check tables/basic/Basic_qv_10_full.tex.md5
rm_check tables/basic/Basic_qv_10_partial_doc.pdf
rm_check tables/basic/Basic_qv_10_partial.tex
rm_check tables/basic/Basic_qv_10_partial.tex.md5
rm_check tables/basic/Basic_qv_30_full_doc.pdf
rm_check tables/basic/Basic_qv_30_full.tex
rm_check tables/basic/Basic_qv_30_full.tex.md5
rm_check tables/basic/Basic_qv_30_partial_doc.pdf
rm_check tables/basic/Basic_qv_30_partial.tex
rm_check tables/basic/Basic_qv_30_partial.tex.md5
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_full_doc.pdf
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_full.tex
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_full.tex.md5
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_partial_doc.pdf
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_partial.tex
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_partial.tex.md5
rm_check tables/basic/Basic_stepc_map_cats_path_full_doc.pdf
rm_check tables/basic/Basic_stepc_map_cats_path_full.tex
rm_check tables/basic/Basic_stepc_map_cats_path_full.tex.md5
rm_check tables/basic/Basic_stepc_map_cats_path_partial_doc.pdf
rm_check tables/basic/Basic_stepc_map_cats_path_partial.tex
rm_check tables/basic/Basic_stepc_map_cats_path_partial.tex.md5
rm_check tables/basic/Basic_stepc_map_cats_reg_full_doc.pdf
rm_check tables/basic/Basic_stepc_map_cats_reg_full.tex
rm_check tables/basic/Basic_stepc_map_cats_reg_full.tex.md5
rm_check tables/basic/Basic_stepc_map_cats_reg_partial_doc.pdf
rm_check tables/basic/Basic_stepc_map_cats_reg_partial.tex
rm_check tables/basic/Basic_stepc_map_cats_reg_partial.tex.md5
rm_check tables/basic/Basic_stepc_map_qv_full_doc.pdf
rm_check tables/basic/Basic_stepc_map_qv_full.tex
rm_check tables/basic/Basic_stepc_map_qv_full.tex.md5
rm_check tables/basic/Basic_stepc_map_qv_partial_doc.pdf
rm_check tables/basic/Basic_stepc_map_qv_partial.tex
rm_check tables/basic/Basic_stepc_map_qv_partial.tex.md5
rm_check tables/basic/BasicSummary_doc.pdf
rm_check tables/basic/BasicSummary.tex
rm_check tables/basic/BasicSummary.tex.md5
rm_check tables/basic/Efficiency_doc.pdf
rm_check tables/basic/Efficiency.tex
rm_check tables/basic/Efficiency.tex.md5
rm_check tables/basic/PercentCleared_doc.pdf
rm_check tables/basic/PercentCleared.tex
rm_check tables/basic/PercentCleared.tex.md5
rm_check tables/basic/PriceDegree_doc.pdf
rm_check tables/basic/PriceDegreeMean_doc.pdf
rm_check tables/basic/PriceDegreeMean.tex
rm_check tables/basic/PriceDegreeMean.tex.md5
rm_check tables/basic/PriceDegree.tex
rm_check tables/basic/PriceDegree.tex.md5
rm_check tables/basic/PriceTerms_doc.pdf
rm_check tables/basic/PriceTerms.tex
rm_check tables/basic/PriceTerms.tex.md5
rm_check tables/basic/Revenue_doc.pdf
rm_check tables/basic/Revenue.tex
rm_check tables/basic/Revenue.tex.md5
rm_check tables/basic/Rounds_doc.pdf
rm_check tables/basic/Rounds.tex
rm_check tables/basic/Rounds.tex.md5
rm_check tables/basic/Runtime_doc.pdf
rm_check tables/basic/Runtime.tex
rm_check tables/basic/Runtime.tex.md5
rm_check tables/basic/StepCMap_doc.pdf
rm_check tables/basic/StepCMap.tex
rm_check tables/basic/StepCMap.tex.md5


rm_check tables/basic/BasicSummary_doc.tex
rm_check tables/basic/Basic_cats_arbitrary_10_full_doc.tex
rm_check tables/basic/Basic_cats_arbitrary_10_partial_doc.tex
rm_check tables/basic/Basic_cats_arbitrary_30_full_doc.tex
rm_check tables/basic/Basic_cats_arbitrary_30_partial_doc.tex
rm_check tables/basic/Basic_cats_path_10_full_doc.tex
rm_check tables/basic/Basic_cats_path_10_partial_doc.tex
rm_check tables/basic/Basic_cats_path_30_full_doc.tex
rm_check tables/basic/Basic_cats_path_30_partial_doc.tex
rm_check tables/basic/Basic_cats_reg_10_full_doc.tex
rm_check tables/basic/Basic_cats_reg_10_partial_doc.tex
rm_check tables/basic/Basic_cats_reg_30_full_doc.tex
rm_check tables/basic/Basic_cats_reg_30_partial_doc.tex
rm_check tables/basic/Basic_qv_10_full_doc.tex
rm_check tables/basic/Basic_qv_10_partial_doc.tex
rm_check tables/basic/Basic_qv_30_full_doc.tex
rm_check tables/basic/Basic_qv_30_partial_doc.tex
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_full_doc.tex
rm_check tables/basic/Basic_stepc_map_cats_arbitrary_partial_doc.tex
rm_check tables/basic/Basic_stepc_map_cats_path_full_doc.tex
rm_check tables/basic/Basic_stepc_map_cats_path_partial_doc.tex
rm_check tables/basic/Basic_stepc_map_cats_reg_full_doc.tex
rm_check tables/basic/Basic_stepc_map_cats_reg_partial_doc.tex
rm_check tables/basic/Basic_stepc_map_qv_full_doc.tex
rm_check tables/basic/Basic_stepc_map_qv_partial_doc.tex
rm_check tables/basic/Efficiency_doc.tex
rm_check tables/basic/PercentCleared_doc.tex
rm_check tables/basic/PriceDegreeMean_doc.tex
rm_check tables/basic/PriceDegree_doc.tex
rm_check tables/basic/PriceTerms_doc.tex
rm_check tables/basic/Revenue_doc.tex
rm_check tables/basic/Rounds_doc.tex
rm_check tables/basic/Runtime_doc.tex
rm_check tables/basic/StepCMap_doc.tex

rm_check tables/strategy/default-Efficiency_doc.pdf
rm_check tables/strategy/default-Efficiency.tex
rm_check tables/strategy/default-Efficiency.tex.md5
rm_check tables/strategy/default-PercentCleared_doc.pdf
rm_check tables/strategy/default-PercentCleared.tex
rm_check tables/strategy/default-PercentCleared.tex.md5
rm_check tables/strategy/default-PriceDegree_doc.pdf
rm_check tables/strategy/default-PriceDegree.tex
rm_check tables/strategy/default-PriceDegree.tex.md5
rm_check tables/strategy/default-PriceTerms_doc.pdf
rm_check tables/strategy/default-PriceTerms.tex
rm_check tables/strategy/default-PriceTerms.tex.md5
rm_check tables/strategy/default-Revenue_doc.pdf
rm_check tables/strategy/default-Revenue.tex
rm_check tables/strategy/default-Revenue.tex.md5
rm_check tables/strategy/default-Rounds_doc.pdf
rm_check tables/strategy/default-Rounds.tex
rm_check tables/strategy/default-Rounds.tex.md5
rm_check tables/strategy/default-Runtime_doc.pdf
rm_check tables/strategy/default-Runtime.tex
rm_check tables/strategy/default-Runtime.tex.md5
rm_check tables/strategy/heuristic-Efficiency_doc.pdf
rm_check tables/strategy/heuristic-Efficiency.tex
rm_check tables/strategy/heuristic-Efficiency.tex.md5
rm_check tables/strategy/heuristic-PercentCleared_doc.pdf
rm_check tables/strategy/heuristic-PercentCleared.tex
rm_check tables/strategy/heuristic-PercentCleared.tex.md5
rm_check tables/strategy/heuristic-PriceDegree_doc.pdf
rm_check tables/strategy/heuristic-PriceDegree.tex
rm_check tables/strategy/heuristic-PriceDegree.tex.md5
rm_check tables/strategy/heuristic-PriceTerms_doc.pdf
rm_check tables/strategy/heuristic-PriceTerms.tex
rm_check tables/strategy/heuristic-PriceTerms.tex.md5
rm_check tables/strategy/heuristic-Revenue_doc.pdf
rm_check tables/strategy/heuristic-Revenue.tex
rm_check tables/strategy/heuristic-Revenue.tex.md5
rm_check tables/strategy/heuristic-Rounds_doc.pdf
rm_check tables/strategy/heuristic-Rounds.tex
rm_check tables/strategy/heuristic-Rounds.tex.md5
rm_check tables/strategy/heuristic-Runtime_doc.pdf
rm_check tables/strategy/heuristic-Runtime.tex
rm_check tables/strategy/heuristic-Runtime.tex.md5

rm_check tables/XorPrices
