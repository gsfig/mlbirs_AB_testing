from translation_model.yandex_translate import yandex_translation


class TranslationService:
    to_translate = ""
    translated = ""

    def translate_query(self, to_translate, langfrom: str = 'pt', langto: str = 'en') -> str:
        """
        translates query
        :param to_translate:
        :param langfrom: string indicating language from
        :param langto: string indicating language to
        :return: translated query
        """
        self.to_translate = to_translate
        # self.translated = "infarction hernia modifier hypothalamospinal tract brodmann"
        # self.translated = bingtranslation(self.toTranslate, langfrom, langto)

        # TODO: translation_model
        self.translated = "Two radiologists independently analyzed the HRCT images of the patients and applied the modified Bhalla score. Intra and interobservers reliability were evaluated according to the correlation coefficient intraclasse (ICC). In cystic fibrosis (CF), chronic bacterial infection is responsible for pulmonary structural damage and progressive respiratory difficulty. Respiratory failures represent 95% of deaths in patients with CF"
        #self.translated = yandex_translation(to_translate,langfrom, langto)
        return self.translated










