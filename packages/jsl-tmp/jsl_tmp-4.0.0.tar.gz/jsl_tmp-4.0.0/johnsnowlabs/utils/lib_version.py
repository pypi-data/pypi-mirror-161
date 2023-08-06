from typing import Optional


class LibVersion:
    """Representation of a library version in format A.B.C
    where elements can digits or X which matches all others digits """

    def __init__(self,
                 major_or_canonical_str: str,
                 minor: Optional[str] = None,
                 patch: Optional[str] = None, ):
        if '.' in major_or_canonical_str:
            splits = major_or_canonical_str.lower().split('.')
            if len(splits) < 3:
                raise ValueError(
                    'When using canonical representation to construct a LibVersion, format A.B.C must be used')
            self.major = splits[0]
            self.minor = splits[1]
            self.patch = splits[2]

        else:
            self.major = major_or_canonical_str
            self.minor = minor
            self.patch = patch

    def equals(self: 'LibVersion', lib2: 'LibVersion') -> bool:
        """
        Compare two LibVersions of format A.B.C , consisting of either Digits 0-9 or X .
        X equals to any other version, i.e.  3.X.X equals 3.5.1
        :param lib2:
        :return:
        """
        if self.major == lib2.major:
            if self.minor == 'x' or lib2.minor == 'x':
                return True

            if self.minor == lib2.minor:
                if self.patch == 'x' or lib2.patch == 'x':
                    return True

                if self.patch == lib2.patch:
                    return True
        return False

    def as_str(self) -> str:
        """Return LibVersion object as canonical str representation"""
        return '.'.join([self.major, self.minor, self.patch])
