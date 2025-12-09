#!/usr/bin/env python3
"""
===========================================================================================
@file       model_card_collector_source_tracked_v1.0.py
@brief      Source-tracked Model Card Collector with parameter count and training data extraction
@details    Combines multiple information sources (predefined data, model cards, metadata,
            and system cards / technical reports) to build a comprehensive overview of
            encoder-only, decoder-only and encoder-decoder language models, including
            transparent source tracking for key information such as parameter counts and
            training data.
@author     MM
@date       05.12.2025
@note       Requires: huggingface_hub, requests, pandas, openpyxl
===========================================================================================
"""

from huggingface_hub import model_info, ModelCard
import pandas as pd
import os
import re
from typing import Dict, Tuple
from datetime import datetime
import time
from model_card_collector_shared import PAPER_SOURCES, ARCHITECTURE_DEFS


"""
===========================================================================================
@class      ModelCollector
@brief      Source-tracked Model Card collector with parameter count and training data extraction.
@details    Uses a hybrid approach (manual curation, model card parsing, metadata and
            official documentation) to obtain as complete information as possible for
            encoder-only, decoder-only and encoder-decoder model families. All extracted
            information is annotated with explicit source references to support
            scientific transparency and reproducibility. Output is written as
            markdown model cards and an aggregated Excel workbook with source overview.
@author     MM
@date       05.12.2025
@note       Output consists of per-model markdown files and an Excel file with
            architecture-specific and combined overviews plus a source summary sheet.
===========================================================================================
"""
class ModelCollector:
   
    """
    ==========================================================================================
    @fn         ModelCollector::ModelCollector()
    @brief      Constructor for the ModelCollector class.
    @details    Initializes the model collector, including the output directory, the current
                access date, predefined paper sources and architecture definitions for all
                supported model families.
    @author     MM
    @date       05.12.2025
    @param[in]  output_dir  Optional path to the model card output directory
                            (default = "model_cards").
    @return     void
    @note       The output directory is created if it does not yet exist. Architecture
                definitions are loaded from ARCHITECTURE_DEFS and paper sources from
                PAPER_SOURCES.
    ==========================================================================================
    """
    def __init__(self, output_dir="model_cards"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.access_date = datetime.now().strftime("%Y-%m-%d")
        
        # Paper-URLs für Primärquellen
        self.paper_sources = PAPER_SOURCES
        
        # Architektur-Definitionen
        self.model_architectures = ARCHITECTURE_DEFS
    
    """
    ==========================================================================================
    @fn         ModelCollector::extract_parameters_from_card()
    @brief      Extract parameter count from a model card.
    @details    Extracts the parameter count for a model from the given model card text using
                a set of regular expression patterns that search for occurrences of parameter
                counts in millions or billions (M/B) together with keywords like
                "parameters" or "params" or "model size". If no explicit parameter count can
                be found in the model card text, the method falls back to simple heuristics
                based on Hugging Face metadata tags (e.g. "7b", "13b", "base", "large").
    @author     MM
    @date       05.12.2025
    @param[in]  card_content  Full textual content of the model card as a single string.
    @param[in]  metadata      Dictionary with additional model metadata (typically taken from
                            the model card data and/or Hugging Face metadata).
    @return     Tuple[str, str]
                A pair (value, source_description) where:
                - value  = textual representation of the parameter information (e.g.
                        "110M parameters", "Inferred from tags: 7b", or a fallback
                        string like "Not specified in Model Card").
                - source_description = short textual description of where the information
                                    was obtained from (e.g. "Extracted from Model Card: …",
                                    "Model metadata tags", or an explanation that no value
                                    was found).
    @note       If the model card is not available, the method returns a descriptive
                placeholder value such as "Not found in Model Card" together with an
                appropriate source description. The method never returns None.
    ==========================================================================================
    """
    def extract_parameters_from_card(self, card_content: str, metadata: dict) -> Tuple[str, str]:

        if not card_content or card_content == "Model Card nicht verfügbar":
            return "Not found in Model Card", "Model Card not available"
        
        # Regex-Patterns
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*[BM]\s+parameters', "Model Card text"),
            (r'parameters[:\s]+(\d+(?:\.\d+)?)\s*[BM]', "Model Card parameters section"),
            (r'(\d+(?:\.\d+)?)[BM]\s+params', "Model Card params mention"),
            (r'model size[:\s]+(\d+(?:\.\d+)?)\s*[BM]', "Model Card size specification"),
        ]
        
        for pattern, source_desc in patterns:
            match = re.search(pattern, card_content, re.IGNORECASE)
            if match:
                value = match.group(0)
                # Finde Kontext (50 Zeichen vor und nach)
                start = max(0, match.start() - 50)
                end = min(len(card_content), match.end() + 50)
                context = card_content[start:end].replace('\n', ' ')
                source = f"{source_desc}: '{context}...'"
                return value, source
        
        # Prüfe Tags
        if 'tags' in metadata and metadata['tags']:
            for tag in metadata['tags']:
                if any(size in str(tag).lower() for size in ['base', 'large', 'small', '7b', '13b', '70b']):
                    return f"Inferred from tags: {tag}", "Model metadata tags"
        
        return "Not specified in Model Card", "Model Card checked, no parameter count found"
    
    """
    ==========================================================================================
    @fn         ModelCollector::extract_training_data_from_card()
    @brief      Extract training data information from a model card.
    @details    Extracts information about the training data from the model card text by
                searching for dedicated "Training Data", "Dataset", "Trained on" or
                "Pre-training data" sections. If no suitable section is found in the card
                itself or the card is not available, the method falls back to the
                'datasets' field in the provided metadata (typically Hugging Face metadata).
                The extracted description from the card is shortened to the first line
                (max. 200 characters) to keep it concise.
    @author     MM
    @date       05.12.2025
    @param[in]  card_content  Full textual content of the model card as a single string.
    @param[in]  metadata      Dictionary with Hugging Face model metadata (e.g. 'datasets').
    @return     Tuple[str, str]
                A pair (value, source_description) where:
                - value  = textual summary of the training data information (either taken
                        from the card text or from the 'datasets' metadata field, or
                        a fallback such as "Not specified in Model Card").
                - source_description = short description of the origin of the information
                                    (e.g. "Model Card: 'Training Data' section",
                                    "Hugging Face metadata: 'datasets' field", or a
                                    corresponding fallback description).
    @note       If the model card is not available and no datasets are present in the
                metadata, the method returns a textual placeholder value such as
                "Not specified" together with a matching source description. The method
                never returns None.
    ==========================================================================================
    """
    def extract_training_data_from_card(self, card_content: str, metadata: dict) -> Tuple[str, str]:
       
        if not card_content or card_content == "Model Card nicht verfügbar":
            # Prüfe Metadaten
            if 'datasets' in metadata and metadata['datasets']:
                datasets = ", ".join(metadata['datasets'][:5])
                return datasets, "Hugging Face metadata: 'datasets' field"
            return "Not specified", "Model Card not available"
        
        # Suche nach Training Data Sections
        sections = [
            (r'## Training Data\s*\n(.{0,500})', "Model Card: 'Training Data' section"),
            (r'## Dataset\s*\n(.{0,500})', "Model Card: 'Dataset' section"),
            (r'Training Data[:\s]+(.{0,300})', "Model Card: Training Data description"),
            (r'Trained on[:\s]+(.{0,300})', "Model Card: Training description"),
            (r'Pre-training data[:\s]+(.{0,300})', "Model Card: Pre-training data section"),
        ]
        
        for pattern, source_desc in sections:
            match = re.search(pattern, card_content, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1).strip()
                # Nehme ersten Satz oder 200 Zeichen
                text = text.split('\n')[0][:200]
                if text:
                    return text, source_desc
        
        # Fallback: Metadaten
        if 'datasets' in metadata and metadata['datasets']:
            datasets = ", ".join(metadata['datasets'][:5])
            return datasets, "Hugging Face metadata: 'datasets' field"
        
        return "Not specified in Model Card", "Model Card checked, no training data info found"
    
    """
    ==========================================================================================
    @fn         ModelCollector::get_paper_reference()
    @brief      Retrieve paper reference metadata for a given model family.
    @details    Looks up the predefined paper reference for the specified model family in
                the internal paper_sources dictionary. For Llama 3.x variants, a special
                fallback to the "Llama-3" (or "Llama") entry is used. If no entry is found,
                a default record with "N/A" fields is returned.@param[in]  family  Name of the model family (e.g. "BERT", "Llama-3").
    @return     Dict
                Dictionary containing paper metadata with at least the keys:
                "paper_url", "paper_title", "authors", and "venue".
    ==========================================================================================
    """
    def get_paper_reference(self, family: str) -> Dict:
        """Holt Paper-Referenz für Modell-Familie"""
        if family in self.paper_sources:
            return self.paper_sources[family]
        
        # Spezialfall: Llama 3.x
        if "llama-3" in family.lower():
            return self.paper_sources.get("Llama-3", self.paper_sources["Llama"])
        
        return {
            "paper_url": "N/A",
            "paper_title": "N/A",
            "authors": "N/A",
            "venue": "N/A"
        }
    
    """
    ==========================================================================================
    @fn         ModelCollector::download_hf_with_sources()
    @brief      Download and enrich a Hugging Face model card with source-tracked metadata.
    @details    Downloads the Hugging Face model information and model card for the specified
                model, extracts parameter count and training data information together with
                explicit source descriptions, resolves the associated paper reference, and
                writes a markdown file containing both the extracted information (including
                sources) and the original model card text. In addition, a structured metadata
                dictionary is returned which is later used to populate the Excel overview.
    @author     MM
    @date       05.12.2025
    @param[in]  model_dict  Dictionary describing the Hugging Face model, containing at
                            least:
                            - "id":      Hugging Face model id (str)
                            - "version": Optional version identifier (str, may be "N/A")
                            - "family":  Model family name (str), added before calling
                                        this method.
    @return     Dict
                Dictionary with enriched metadata for the model, including fields such as:
                - "Modellname", "Version", "Architektur", "Anzahl Parameter",
                "Parameter Quelle", "Trainingsbasis", "Training Data Quelle",
                "Organisation", "Downloads", "Likes", "Pipeline Task",
                "Library", "Tags", "Erstellt", "Letzte Änderung",
                "Zugriffsdatum", "Model Card Datei", "Model Card URL",
                "Paper Titel", "Paper Authors", "Paper URL",
                "Lizenz", "Sprache" and others.
                In case of an error, a dictionary with at least "Modellname", "Fehler"
                and "Zugriffsdatum" is returned instead.
    @note       Architecture type and additional descriptors (such as model family,
                description and year) are added later in collect_all_architectures().
                The markdown file is stored in the configured output directory, using
                the model id and access date in the filename.
    ==========================================================================================
    """
    def download_hf_with_sources(self, model_dict: Dict) -> Dict:
        """Lädt Model Card und extrahiert Informationen mit Quellenangaben"""
        model_id = model_dict["id"]
        family = model_dict.get("family", "Unknown")
        
        try:
            print(f"  📥 {model_id}")
            
            # Model Info
            info = model_info(model_id)
            
            # Model Card
            try:
                card = ModelCard.load(model_id)
                card_content = card.content
                card_metadata = card.data.to_dict() if hasattr(card.data, 'to_dict') else {}
            except:
                card_content = "Model Card nicht verfügbar"
                card_metadata = {}
            
            # Extrahiere Parameter MIT Quelle
            params, params_source = self.extract_parameters_from_card(card_content, card_metadata)
            
            # Extrahiere Training Data MIT Quelle
            training, training_source = self.extract_training_data_from_card(card_content, card_metadata)
            
            # Paper-Referenz
            paper_ref = self.get_paper_reference(family)
            
            # Datetime-Konvertierung
            last_modified = getattr(info, 'lastModified', None)
            created_at = getattr(info, 'createdAt', None)
            
            if last_modified is not None:
                last_modified = str(last_modified.replace(tzinfo=None)) if hasattr(last_modified, 'replace') else str(last_modified)
            
            if created_at is not None:
                created_at = str(created_at.replace(tzinfo=None)) if hasattr(created_at, 'replace') else str(created_at)
            
            # Speichere Model Card mit Quellenangaben
            filename = f"{model_id.replace('/', '_')}_{self.access_date}.md"
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Model Card für {model_id}\n\n")
                f.write(f"## Metadaten\n")
                f.write(f"- **Zugriffsdatum**: {self.access_date}\n")
                f.write(f"- **Version**: {model_dict.get('version', 'N/A')}\n")
                f.write(f"- **Hugging Face URL**: https://huggingface.co/{model_id}\n\n")
                
                f.write(f"## Extrahierte Informationen\n\n")
                f.write(f"### Parameter\n")
                f.write(f"- **Wert**: {params}\n")
                f.write(f"- **Quelle**: {params_source}\n\n")
                
                f.write(f"### Training Data\n")
                f.write(f"- **Wert**: {training}\n")
                f.write(f"- **Quelle**: {training_source}\n\n")
                
                f.write(f"## Paper-Referenz\n")
                f.write(f"- **Title**: {paper_ref['paper_title']}\n")
                f.write(f"- **Authors**: {paper_ref['authors']}\n")
                f.write(f"- **Venue**: {paper_ref['venue']}\n")
                f.write(f"- **URL**: {paper_ref['paper_url']}\n\n")
                
                f.write(f"---\n\n")
                f.write(f"## Original Model Card\n\n")
                f.write(card_content)
            
            data = {
                "Modellname": info.modelId,
                "Version": model_dict.get("version", "N/A"),
                "Architektur": self.classify_architecture(model_id),
                "Anzahl Parameter": params,
                "Parameter Quelle": params_source,
                "Trainingsbasis": training,
                "Training Data Quelle": training_source,
                "Organisation": info.author or "Unknown",
                "Downloads": getattr(info, 'downloads', 0),
                "Likes": getattr(info, 'likes', 0),
                "Pipeline Task": getattr(info, 'pipeline_tag', "N/A") or "N/A",
                "Library": getattr(info, 'library_name', "N/A") or "N/A",
                "Tags": ", ".join(info.tags[:5]) if info.tags else "N/A",
                "Erstellt": created_at or "N/A",
                "Letzte Änderung": last_modified or "N/A",
                "Zugriffsdatum": self.access_date,
                "Model Card Datei": filename,
                "Quelle": "Hugging Face",
                "Model Card URL": f"https://huggingface.co/{model_id}",
                "Paper Titel": paper_ref['paper_title'],
                "Paper Authors": paper_ref['authors'],
                "Paper URL": paper_ref['paper_url'],
                "Lizenz": card_metadata.get('license', 'N/A'),
                "Sprache": card_metadata.get('language', 'N/A')
            }
            
            print(f"    ✓ Gespeichert (Params: {params})")
            return data
            
        except Exception as e:
            print(f"    ✗ Fehler: {str(e)}")
            return {
                "Modellname": model_id,
                "Fehler": str(e),
                "Zugriffsdatum": self.access_date
            }
    
    """
    ==========================================================================================
    @fn         ModelCollector::download_proprietary_model_with_sources()
    @brief      Create a source-tracked metadata record for proprietary models.
    @details    Builds a metadata dictionary for proprietary or closed-source model families
                (e.g. GPT-4, Gemini, Claude) based on the predefined architecture
                definitions (ARCHITECTURE_DEFS), version information and associated paper or
                system card references. No Hugging Face API calls or markdown model card
                files are produced here; instead, information is taken from official
                documentation and technical reports.@author     MM
    @date       05.12.2025
    @param[in]  model_family  Name of the model family (e.g. "GPT-4", "Llama-3") used as
                            key in the architecture definitions.
    @param[in]  version_info  Dictionary describing a specific version/release of the
                            proprietary model family, typically containing at least:
                            - "name":     Version or variant name
                            - "released": Release date or release identifier.
    @return     Dict
                Dictionary with metadata for the proprietary model, including fields such as
                "Modellname", "Version", "Architektur", "Anzahl Parameter",
                "Parameter Quelle", "Trainingsbasis", "Training Data Quelle",
                "Organisation", "Release-Datum", "Zugriffsdatum", "Quelle",
                "Model Card URL", "Paper Titel", "Paper Authors" and "Paper URL".
                In case of an error, a dictionary with "Modellname", "Fehler" and
                "Zugriffsdatum" is returned instead.
    @note       Architecture type, family description and year are enriched later in
                collect_all_architectures(). Parameter counts for proprietary models are
                typically marked as "Not disclosed" with a corresponding source description.
    ==========================================================================================
    """
    def download_proprietary_model_with_sources(self, model_family: str, version_info: Dict) -> Dict:
        """Lädt proprietäre Model Card mit Quellenangaben"""
        try:
            model_name = version_info['name']
            print(f"  📥 {model_family} - {model_name}")
            
            # Paper-Referenz
            paper_ref = self.get_paper_reference(model_family)
            
            data = {
                "Modellname": model_name,
                "Version": model_name,
                "Architektur": self.model_architectures[model_family]["architecture"],
                "Anzahl Parameter": "Not disclosed",
                "Parameter Quelle": f"Not disclosed by {self.model_architectures[model_family]['organization']}",
                "Trainingsbasis": f"See {paper_ref['paper_title']} for general description",
                "Training Data Quelle": f"System Card / Technical Report: {paper_ref['paper_url']}",
                "Organisation": self.model_architectures[model_family]["organization"],
                "Release-Datum": version_info['released'],
                "Zugriffsdatum": self.access_date,
                "Quelle": "Official Documentation",
                "Model Card URL": "N/A (proprietary)",
                "Paper Titel": paper_ref['paper_title'],
                "Paper Authors": paper_ref['authors'],
                "Paper URL": paper_ref['paper_url']
            }
            
            print(f"    ✓ {model_name}")
            return data
            
        except Exception as e:
            print(f"    ✗ Fehler: {str(e)}")
            return {
                "Modellname": f"{model_family} - {version_info.get('name', 'Unknown')}",
                "Fehler": str(e),
                "Zugriffsdatum": self.access_date
            }
    
    """
    ==========================================================================================
    @fn         ModelCollector::classify_architecture()
    @brief      Infer architecture type from model name.
    @details    Infers the architecture type (encoder-only, decoder-only, encoder-decoder)
                for a given model name by matching it against the known model families
                defined in the architecture dictionary. Matching is performed via
                case-insensitive substring search on the family name within the provided
                model name.@author     MM
    @date       05.12.2025
    @param[in]  model_name  Full model identifier (e.g. Hugging Face id or proprietary
                            model name) used to infer the architecture.
    @return     str
                String with the architecture class (e.g. "Encoder-only", "Decoder-only",
                "Encoder-Decoder") or "Unknown" if no match is found.
    @note       This method relies on consistent family naming in the architecture
                definitions. It does not query external services.
    ==========================================================================================
    """
    def classify_architecture(self, model_name: str) -> str:
        """Bestimmt die Architekturklasse"""
        for family, info in self.model_architectures.items():
            if family.lower() in model_name.lower():
                return info["architecture"]
        return "Unknown"
    
    """
    ==========================================================================================
    @fn         ModelCollector::collect_all_architectures()
    @brief      Collect metadata for all configured model families grouped by architecture.
    @details    Iterates over all defined model families in the architecture dictionary and
                collects enriched metadata for both Hugging Face and proprietary models.
                Hugging Face models are processed via download_hf_with_sources(), whereas
                proprietary models are handled by download_proprietary_model_with_sources().
                Results are grouped into three categories (encoder-only, decoder-only,
                encoder-decoder) and returned as three separate pandas DataFrames. Progress
                information is printed to stdout and small delays are introduced to
                reduce the risk of hitting API rate limits.@author     MM
    @date       05.12.2025
    @return     Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
                A tuple of three pandas DataFrames:
                (df_encoder_only, df_decoder_only, df_encoder_decoder), where each
                DataFrame contains one row per collected model of the corresponding
                architecture type. Empty DataFrames are returned if no models are
                available for a given category.
    @note       Additional family-level descriptors such as "Modell-Familie",
                "Beschreibung" and "Jahr" are added to each record within this method.
                Proprietary models are currently added to the decoder-only group if
                their architecture is marked as "Decoder-only" in the definitions.
    ==========================================================================================
    """
    def collect_all_architectures(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Sammelt alle Modelle mit Quellenangaben"""
        
        encoder_only = []
        decoder_only = []
        encoder_decoder = []
        
        print("="*80)
        print("SOURCE-TRACKED MODEL CARD COLLECTOR")
        print("Alle Informationen mit transparenten Quellenangaben")
        print("="*80)
        print(f"Zugriffsdatum: {self.access_date}")
        print()
        
        for family, info in self.model_architectures.items():
            print(f"\n{'='*80}")
            print(f"📦 {family} ({info['architecture']})")
            print(f"   Organisation: {info['organization']}")
            print(f"   Jahr: {info['year']}")
            print('-'*80)
            
            arch_type = info["architecture"]
            
            # Hugging Face Modelle
            if "huggingface" in info:
                for model_dict in info["huggingface"]:
                    model_dict["family"] = family
                    data = self.download_hf_with_sources(model_dict)
                    data["Modell-Familie"] = family
                    data["Beschreibung"] = info["description"]
                    data["Jahr"] = info["year"]
                    
                    if arch_type == "Encoder-only":
                        encoder_only.append(data)
                    elif arch_type == "Decoder-only":
                        decoder_only.append(data)
                    elif arch_type == "Encoder-Decoder":
                        encoder_decoder.append(data)
                    
                    time.sleep(0.5)
            
            # Proprietäre Modelle
            if "versions" in info:
                for version in info["versions"]:
                    data = self.download_proprietary_model_with_sources(family, version)
                    data["Modell-Familie"] = family
                    data["Beschreibung"] = info["description"]
                    data["Jahr"] = info["year"]
                    
                    if arch_type == "Decoder-only":
                        decoder_only.append(data)
        
        # Erstelle DataFrames
        df_encoder = pd.DataFrame(encoder_only) if encoder_only else pd.DataFrame()
        df_decoder = pd.DataFrame(decoder_only) if decoder_only else pd.DataFrame()
        df_enc_dec = pd.DataFrame(encoder_decoder) if encoder_decoder else pd.DataFrame()
        
        return df_encoder, df_decoder, df_enc_dec
    
    """
    ==========================================================================================
    @fn         ModelCollector::export_comprehensive_overview()
    @brief      Export a comprehensive Excel workbook with source-tracked model overviews.
    @details    Exports a comprehensive Excel workbook that summarizes all collected models.
                The workbook contains one sheet per architecture type ("Encoder-only",
                "Decoder-only", "Encoder-Decoder"), an aggregated "Alle Modelle" sheet that
                combines all architectures, and a "Quellenübersicht" sheet that lists
                parameter and training data values together with their corresponding
                source descriptions and paper URLs. All NaN values are converted to "N/A"
                before exporting to ensure a clean representation in Excel.@author     MM
    @date       05.12.2025
    @param[in]  df_encoder   DataFrame with encoder-only models.
    @param[in]  df_decoder   DataFrame with decoder-only models.
    @param[in]  df_enc_dec   DataFrame with encoder-decoder models.
    @return     str
                Full path to the generated Excel file containing all exported sheets.
    @note       The "Quellenübersicht" sheet summarizes for each model which values for
                "Anzahl Parameter" and "Trainingsbasis" were used and from which sources
                they were derived (e.g. Model Card, metadata, paper URL). All numeric and
                non-string values in the DataFrames are converted to strings before export
                and occurrences of "nan" are replaced by "N/A".
    ==========================================================================================
    """
    def export_comprehensive_overview(self, df_encoder, df_decoder, df_enc_dec):
        """Erstellt Excel mit Quellenangaben"""
        
        # Bereinige DataFrames
        for df in [df_encoder, df_decoder, df_enc_dec]:
            if not df.empty:
                for col in df.columns:
                    try:
                        df[col] = df[col].astype(str).replace('nan', 'N/A')
                    except:
                        df[col] = df[col].apply(lambda x: str(x) if x is not None else "N/A")
        
        output_file = os.path.join(self.output_dir, 
                                   f"Model_Cards_SourceTracked_{self.access_date}.xlsx")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Sheets nach Architektur
            if not df_encoder.empty:
                df_encoder.to_excel(writer, sheet_name='Encoder-only', index=False)
            
            if not df_decoder.empty:
                df_decoder.to_excel(writer, sheet_name='Decoder-only', index=False)
            
            if not df_enc_dec.empty:
                df_enc_dec.to_excel(writer, sheet_name='Encoder-Decoder', index=False)
            
            # Alle kombiniert
            all_models = pd.concat([df_encoder, df_decoder, df_enc_dec], ignore_index=True)
            if not all_models.empty:
                all_models.to_excel(writer, sheet_name='Alle Modelle', index=False)
            
            # Quellenübersicht
            sources_data = []
            for _, row in all_models.iterrows():
                if "Anzahl Parameter" in row and row["Anzahl Parameter"] != "N/A":
                    sources_data.append({
                        "Modell": row.get("Modellname", "N/A"),
                        "Information": "Parameter",
                        "Wert": row.get("Anzahl Parameter", "N/A"),
                        "Quelle": row.get("Parameter Quelle", "N/A"),
                        "Paper URL": row.get("Paper URL", "N/A")
                    })
                if "Trainingsbasis" in row and row["Trainingsbasis"] != "N/A":
                    sources_data.append({
                        "Modell": row.get("Modellname", "N/A"),
                        "Information": "Training Data",
                        "Wert": row.get("Trainingsbasis", "N/A")[:100],  # Gekürzt
                        "Quelle": row.get("Training Data Quelle", "N/A"),
                        "Paper URL": row.get("Paper URL", "N/A")
                    })
            
            if sources_data:
                df_sources = pd.DataFrame(sources_data)
                df_sources.to_excel(writer, sheet_name='Quellenübersicht', index=False)
        
        print(f"\n{'='*80}")
        print(f"✅ Excel-Datei erstellt: {output_file}")
        print(f"   MIT TRANSPARENTEN QUELLENANGABEN für:")
        print(f"   ✓ Anzahl Parameter (inkl. Quelle)")
        print(f"   ✓ Trainingsbasis (inkl. Quelle)")
        print(f"   ✓ Paper-Referenzen (URLs)")
        print(f"   Zugriffsdatum: {self.access_date}")
        print('='*80)
        
        return output_file

"""
==========================================================================================
@fn         main()
@brief      Command line entry point for the source-tracked Model Card Collector.
@details    Provides a simple command line interaction: it prints a description of the
            source-tracked model card collection process, asks the user for confirmation
            via standard input, and if confirmed, triggers the collection of all
            architectures and the export of the comprehensive Excel overview. If the
            user declines, the script terminates without performing any network
            requests.@author     MM
@date       05.12.2025
@return     void
@note       Requires a working internet connection and the huggingface_hub package.
            When this script is executed as __main__, a basic import check for
            huggingface_hub is performed and a helpful installation hint is printed
            if the package is missing.
==========================================================================================
"""
def main():
    print("\n" + "="*80)
    print("SOURCE-TRACKED MODEL CARD COLLECTOR")
    print("Transparente Quellenangaben für wissenschaftliche Arbeiten")
    print("="*80)
    print("""
    Dieses Script extrahiert Informationen DIREKT aus verifizierbaren Quellen:

    ✓ Model Cards (Hugging Face)
    ✓ Research Papers (ArXiv, Venues)
    ✓ System Cards (OpenAI, Anthropic, Google)

    JEDE INFORMATION wird mit Quelle dokumentiert:
    - "Extracted from Model Card: 'This model has 110M parameters...'"
    - "Hugging Face metadata: 'datasets' field"
    - "Paper: BERT (Devlin et al., 2019) - https://arxiv.org/..."

    EXCEL ENTHÄLT:
    - Spalte "Parameter Quelle"
    - Spalte "Training Data Quelle"
    - Spalte "Paper URL"
    - Sheet "Quellenübersicht"

    → Wissenschaftlich nachvollziehbar und zitierbar!
        """)
    
   
    collector = ModelCollector()
    
    print("\n⏳ Sammle Model Cards mit Quellenangaben...")
    df_encoder, df_decoder, df_enc_dec = collector.collect_all_architectures()
    
    print("\n📊 Erstelle Excel-Übersicht mit Quellen...")
    output_file = collector.export_comprehensive_overview(df_encoder, df_decoder, df_enc_dec)
    
    print(f"\n✅ Fertig! Datei: {output_file}")
    print("\n📋 Prüfen Sie das Sheet 'Quellenübersicht' für alle Quellenangaben!")
        
   

if __name__ == "__main__":
    try:
        import huggingface_hub
        main()
    except ImportError:
        print("""
❌ FEHLER: huggingface_hub nicht installiert

Installieren Sie mit:
    pip install huggingface_hub requests pandas openpyxl
        """)
