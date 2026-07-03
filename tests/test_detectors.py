from mal_gui.detectors import parse_detector_index_from_mal


def test_parse_detector_index_from_mal_marks_assets_with_detectors():
    detector_index = parse_detector_index_from_mal(
        """
        category Demo {
          asset Application {
            ! logSignedin (authenticatesPrincipal.compromised AccessKey) [fpr: 0.3, tpr: 0.98]
          }

          asset AccessKey {
            | compromised
          }
        }
        """
    )

    assert detector_index.has_detector("Application")
    assert not detector_index.has_detector("AccessKey")


def test_parse_detector_index_from_mal_ignores_comments_and_assets_without_detectors():
    detector_index = parse_detector_index_from_mal(
        """
        category Demo {
          asset Identity {
            // ! ignoredDetector (compromised) [fpr: 0.5, tpr: 0.5]
          }

          asset Credentials
          {
            ! credentialSignal (read) [fpr: 0.1, tpr: 0.9]
          }
        }
        """
    )

    assert detector_index.has_detector("Credentials")
    assert not detector_index.has_detector("Identity")
