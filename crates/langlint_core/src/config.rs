use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

/// Langlint configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub include: Vec<String>,

    #[serde(default)]
    pub exclude: Vec<String>,

    #[serde(default = "default_source_lang")]
    pub source_lang: Vec<String>,

    #[serde(default = "default_target_lang")]
    pub target_lang: String,

    #[serde(default = "default_translator")]
    pub translator: String,

    #[serde(default)]
    pub dry_run: bool,

    #[serde(default = "default_backup")]
    pub backup: bool,
}

fn default_source_lang() -> Vec<String> {
    vec!["auto".to_string()]
}

fn default_target_lang() -> String {
    "en".to_string()
}

fn default_translator() -> String {
    "google".to_string()
}

fn default_backup() -> bool {
    true
}

impl Default for Config {
    fn default() -> Self {
        Self {
            include: Vec::new(),
            exclude: Vec::new(),
            source_lang: default_source_lang(),
            target_lang: default_target_lang(),
            translator: default_translator(),
            dry_run: false,
            backup: default_backup(),
        }
    }
}

impl Config {
    /// Load configuration from a file
    pub fn load_from_file(path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let content = fs::read_to_string(path)
            .with_context(|| format!("Failed to read config file: {}", path.display()))?;

        let config = if path.extension().and_then(|s| s.to_str()) == Some("toml") {
            toml::from_str(&content)?
        } else if path.extension().and_then(|s| s.to_str()) == Some("yaml")
            || path.extension().and_then(|s| s.to_str()) == Some("yml")
        {
            serde_yaml::from_str(&content)?
        } else {
            anyhow::bail!("Unsupported config file format: {}", path.display());
        };

        Ok(config)
    }

    /// Try to find and load configuration from common locations
    pub fn find_and_load() -> Result<Self> {
        let config_files = [
            ".langlint.yml",
            ".langlint.yaml",
            "langlint.toml",
            "pyproject.toml",
        ];

        for config_file in &config_files {
            let path = PathBuf::from(config_file);
            if path.exists() {
                if config_file == &"pyproject.toml" {
                    return Self::load_from_pyproject(&path);
                } else {
                    return Self::load_from_file(&path);
                }
            }
        }

        // No config file found, use defaults
        Ok(Self::default())
    }

    /// Load configuration from pyproject.toml [tool.langlint] section
    fn load_from_pyproject(path: &Path) -> Result<Self> {
        let content = fs::read_to_string(path)?;
        let pyproject: toml::Value = toml::from_str(&content)?;

        if let Some(tool) = pyproject.get("tool") {
            if let Some(langlint) = tool.get("langlint") {
                let config: Config = langlint.clone().try_into()?;
                return Ok(config);
            }
        }

        // No [tool.langlint] section, use defaults
        Ok(Self::default())
    }

    /// Merge this config with another, preferring values from `other`
    pub fn merge(mut self, other: Config) -> Self {
        if !other.include.is_empty() {
            self.include = other.include;
        }
        if !other.exclude.is_empty() {
            self.exclude = other.exclude;
        }
        if other.source_lang != default_source_lang() {
            self.source_lang = other.source_lang;
        }
        if other.target_lang != default_target_lang() {
            self.target_lang = other.target_lang;
        }
        if other.translator != default_translator() {
            self.translator = other.translator;
        }
        if other.dry_run {
            self.dry_run = other.dry_run;
        }
        if other.backup != default_backup() {
            self.backup = other.backup;
        }
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_default_config() {
        let config = Config::default();
        assert_eq!(config.translator, "google");
        assert_eq!(config.target_lang, "en");
        assert_eq!(config.source_lang, vec!["auto"]);
        assert!(config.backup);
        assert!(!config.dry_run);
    }

    #[test]
    fn test_config_merge() {
        let base = Config::default();
        let override_config = Config {
            translator: "openai".to_string(),
            target_lang: "zh-CN".to_string(),
            ..Config::default()
        };

        let merged = base.merge(override_config);
        assert_eq!(merged.translator, "openai");
        assert_eq!(merged.target_lang, "zh-CN");
    }

    #[test]
    fn test_config_merge_include_exclude() {
        let base = Config::default();
        let override_config = Config {
            include: vec!["**/*.py".to_string()],
            exclude: vec!["**/test_*.py".to_string()],
            ..Config::default()
        };

        let merged = base.merge(override_config);
        assert_eq!(merged.include, vec!["**/*.py"]);
        assert_eq!(merged.exclude, vec!["**/test_*.py"]);
    }

    #[test]
    fn test_config_merge_dry_run() {
        let base = Config::default();
        let override_config = Config {
            dry_run: true,
            ..Config::default()
        };

        let merged = base.merge(override_config);
        assert!(merged.dry_run);
    }

    #[test]
    fn test_config_merge_backup() {
        let base = Config::default();
        let override_config = Config {
            backup: false,
            ..Config::default()
        };

        let merged = base.merge(override_config);
        assert!(!merged.backup);
    }

    #[test]
    fn test_config_serialization() {
        let config = Config::default();
        let json = serde_json::to_string_pretty(&config).unwrap();
        let deserialized: Config = serde_json::from_str(&json).unwrap();

        assert_eq!(config.translator, deserialized.translator);
        assert_eq!(config.target_lang, deserialized.target_lang);
    }

    #[test]
    fn test_config_toml_serialization() {
        let config = Config {
            translator: "openai".to_string(),
            target_lang: "zh-CN".to_string(),
            source_lang: vec!["en".to_string()],
            dry_run: true,
            backup: false,
            include: vec!["*.py".to_string()],
            exclude: vec!["test_*.py".to_string()],
        };

        let toml_str = toml::to_string(&config).unwrap();
        let deserialized: Config = toml::from_str(&toml_str).unwrap();

        assert_eq!(config.translator, deserialized.translator);
        assert_eq!(config.target_lang, deserialized.target_lang);
        assert_eq!(config.dry_run, deserialized.dry_run);
    }

    #[test]
    fn test_load_from_yaml() {
        let temp_dir = TempDir::new().unwrap();
        let config_path = temp_dir.path().join("test.yaml");

        let yaml_content = r#"
translator: openai
target_lang: zh-CN
source_lang:
  - en
  - fr
dry_run: true
backup: false
"#;

        fs::write(&config_path, yaml_content).unwrap();

        let config = Config::load_from_file(&config_path).unwrap();
        assert_eq!(config.translator, "openai");
        assert_eq!(config.target_lang, "zh-CN");
        assert_eq!(config.source_lang, vec!["en", "fr"]);
        assert!(config.dry_run);
        assert!(!config.backup);
    }

    #[test]
    fn test_load_from_toml() {
        let temp_dir = TempDir::new().unwrap();
        let config_path = temp_dir.path().join("test.toml");

        let toml_content = r#"
translator = "deepl"
target_lang = "ja"
source_lang = ["en"]
dry_run = false
backup = true
"#;

        fs::write(&config_path, toml_content).unwrap();

        let config = Config::load_from_file(&config_path).unwrap();
        assert_eq!(config.translator, "deepl");
        assert_eq!(config.target_lang, "ja");
        assert_eq!(config.source_lang, vec!["en"]);
        assert!(!config.dry_run);
        assert!(config.backup);
    }

    #[test]
    fn test_load_unsupported_format() {
        let temp_dir = TempDir::new().unwrap();
        let config_path = temp_dir.path().join("test.json");

        fs::write(&config_path, "{}").unwrap();

        let result = Config::load_from_file(&config_path);
        assert!(result.is_err());
    }

    #[test]
    fn test_load_nonexistent_file() {
        let result = Config::load_from_file("/nonexistent/config.yaml");
        assert!(result.is_err());
    }

    #[test]
    fn test_find_and_load_no_config() {
        // Save current directory
        let current_dir = std::env::current_dir().unwrap();

        // Change to a temporary directory with no config files
        let temp_dir = TempDir::new().unwrap();
        std::env::set_current_dir(temp_dir.path()).unwrap();

        let config = Config::find_and_load().unwrap();
        assert_eq!(config.translator, "google"); // Should use defaults

        // Restore directory
        std::env::set_current_dir(current_dir).unwrap();
    }

    #[test]
    fn test_default_functions() {
        assert_eq!(default_source_lang(), vec!["auto".to_string()]);
        assert_eq!(default_target_lang(), "en");
        assert_eq!(default_translator(), "google");
        assert!(default_backup());
    }

    #[test]
    fn test_config_clone() {
        let config = Config::default();
        let cloned = config.clone();

        assert_eq!(config.translator, cloned.translator);
        assert_eq!(config.target_lang, cloned.target_lang);
    }

    #[test]
    fn test_config_debug() {
        let config = Config::default();
        let debug_str = format!("{:?}", config);

        assert!(debug_str.contains("Config"));
        assert!(debug_str.contains("google"));
    }
}
