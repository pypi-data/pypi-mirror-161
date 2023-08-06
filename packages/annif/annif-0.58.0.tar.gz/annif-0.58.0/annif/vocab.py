"""Vocabulary management functionality for Annif"""

import os.path
import annif
import annif.corpus
import annif.util
from annif.datadir import DatadirMixin
from annif.exception import NotInitializedException

logger = annif.logger


class AnnifVocabulary(DatadirMixin):
    """Class representing a subject vocabulary which can be used by multiple
    Annif projects."""

    # defaults for uninitialized instances
    _subjects = None

    def __init__(self, vocab_id, datadir, language):
        DatadirMixin.__init__(self, datadir, 'vocabs', vocab_id)
        self.vocab_id = vocab_id
        self.language = language
        self._skos_vocab = None

    def _create_subject_index(self, subject_corpus):
        self._subjects = annif.corpus.SubjectIndex(subject_corpus)
        annif.util.atomic_save(self._subjects, self.datadir, 'subjects')

    def _update_subject_index(self, subject_corpus):
        old_subjects = self.subjects
        new_subjects = annif.corpus.SubjectIndex(subject_corpus)
        updated_subjects = annif.corpus.SubjectIndex()

        for uri, label, notation in old_subjects:
            if new_subjects.contains_uri(uri):
                label, notation = new_subjects[new_subjects.by_uri(uri)][1:3]
            else:  # subject removed from new corpus
                label, notation = None, None
            updated_subjects.append(uri, label, notation)
        for uri, label, notation in new_subjects:
            if not old_subjects.contains_uri(uri):
                updated_subjects.append(uri, label, notation)
        self._subjects = updated_subjects
        annif.util.atomic_save(self._subjects, self.datadir, 'subjects')

    @property
    def subjects(self):
        if self._subjects is None:
            path = os.path.join(self.datadir, 'subjects')
            if os.path.exists(path):
                logger.debug('loading subjects from %s', path)
                self._subjects = annif.corpus.SubjectIndex.load(path)
            else:
                raise NotInitializedException(
                    "subject file {} not found".format(path))
        return self._subjects

    @property
    def skos(self):
        """return the subject vocabulary from SKOS file"""
        if self._skos_vocab is not None:
            return self._skos_vocab

        # attempt to load graph from dump file
        dumppath = os.path.join(self.datadir, 'subjects.dump.gz')
        if os.path.exists(dumppath):
            logger.debug(f'loading graph dump from {dumppath}')
            try:
                self._skos_vocab = annif.corpus.SubjectFileSKOS(dumppath,
                                                                self.language)
            except ModuleNotFoundError:
                # Probably dump has been saved using a different rdflib version
                logger.debug('could not load graph dump, using turtle file')
            else:
                return self._skos_vocab

        # graph dump file not found - parse ttl file instead
        path = os.path.join(self.datadir, 'subjects.ttl')
        if os.path.exists(path):
            logger.debug(f'loading graph from {path}')
            self._skos_vocab = annif.corpus.SubjectFileSKOS(path,
                                                            self.language)
            # store the dump file so we can use it next time
            self._skos_vocab.save_skos(path, self.language)
            return self._skos_vocab

        raise NotInitializedException(f'graph file {path} not found')

    def load_vocabulary(self, subject_corpus, language, force=False):
        """Load subjects from a subject corpus and save them into a
        SKOS/Turtle file for later use. If force=True, replace the
        existing vocabulary completely."""

        if not force and os.path.exists(os.path.join(self.datadir,
                                                     'subjects')):
            logger.info('updating existing vocabulary')
            self._update_subject_index(subject_corpus)
        else:
            self._create_subject_index(subject_corpus)
        subject_corpus.save_skos(os.path.join(self.datadir, 'subjects.ttl'),
                                 language)

    def as_skos_file(self):
        """return the vocabulary as a file object, in SKOS/Turtle syntax"""
        return open(os.path.join(self.datadir, 'subjects.ttl'), 'rb')

    def as_graph(self):
        """return the vocabulary as an rdflib graph"""
        return self.skos.graph
