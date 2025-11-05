from pathlib import Path

from py4swiss.trf.codes import PlayerCode, TeamCode, TournamentCode, XCode
from py4swiss.trf.exceptions import LineException, ParsingException
from py4swiss.trf.parsed_trf import ParsedTrf
from py4swiss.trf.sections import PlayerSection, TeamSection


class TrfParser:
    """Parser for TRF(x) files as defined by FIDE and javafo."""

    @staticmethod
    def _parse_line_player(trf: ParsedTrf, _: PlayerCode, line: str) -> None:
        """Parse a line containing a player code (xx1)."""
        if len(line) < 89:
            raise LineException("Player section line is incomplete")

        player_section = PlayerSection()
        player_section.set_code(line)
        player_section.set_starting_number(line)
        player_section.set_sex(line)
        player_section.set_title(line)
        player_section.set_name(line)
        player_section.set_fide_rating(line)
        player_section.set_fide_federation(line)
        player_section.set_fide_number(line)
        player_section.set_birth_date(line)
        player_section.set_points_times_ten(line)
        player_section.set_rank(line)
        player_section.set_results(line)

        for i in (3, 8, 13, 47, 52, 56, 68, 79, 84):
            if line[i] != " ":
                raise LineException("Column of the player section line must be blank", column=i + 1)

        trf.player_sections.append(player_section)

    @staticmethod
    def _parse_line_tournament(trf: ParsedTrf, code: TournamentCode, line: str) -> None:
        """Parse a line containing a tournament code (xx2)."""
        if len(line) < 5 or not bool(line[5:].strip()):
            return
        section = line[5:]

        match code:
            case TournamentCode.TOURNAMENT_NAME:
                trf.tournament_section.tournament_name = section
            case TournamentCode.CITY:
                trf.tournament_section.city = section
            case TournamentCode.FEDERATION:
                trf.tournament_section.federation = section
            case TournamentCode.DATE_OF_START:
                trf.tournament_section.date_of_start = section
            case TournamentCode.DATE_OF_END:
                trf.tournament_section.date_of_end = section
            case TournamentCode.NUMBER_OF_PLAYERS:
                trf.tournament_section.number_of_players = section
            case TournamentCode.NUMBER_OF_RATED_PLAYERS:
                trf.tournament_section.number_of_rated_players = section
            case TournamentCode.NUMBER_OF_TEAMS:
                trf.tournament_section.number_of_teams = section
            case TournamentCode.TYPE_OF_TOURNAMENT:
                trf.tournament_section.type_of_tournament = section
            case TournamentCode.CHIEF_ARBITER:
                trf.tournament_section.chief_arbiter = section
            case TournamentCode.DEPUTY_CHIEF_ARBITER:
                trf.tournament_section.deputy_chief_arbiter = section
            case TournamentCode.ALLOTTED_TIMES_PER_GAME_MOVE:
                trf.tournament_section.alloted_time_per_moves_game = section
            case TournamentCode.DATES_OF_THE_ROUND:
                trf.tournament_section.set_dates_of_the_round(line)

    @staticmethod
    def _parse_line_team(trf: ParsedTrf, _: TeamCode, line: str) -> None:
        """Parse a line containing a team code (xx3)."""
        team_section = TeamSection()

        team_section.set_code(line)
        team_section.set_team_name(line)
        team_section.set_team_players(line)

        trf.team_sections.append(team_section)

    @staticmethod
    def _parse_line_x(trf: ParsedTrf, code: XCode, line: str) -> None:
        """Parse a line containing a javafo specific code (XXx)."""
        match code:
            case XCode.ROUNDS:
                trf.x_section.set_number_of_rounds(line)
            case XCode.ZEROED_IDS:
                for section in line.split()[1:]:
                    trf.x_section.add_zeroed_id(section)
            case XCode.POINT_SYSTEM:
                for section in line.split()[1:]:
                    trf.x_section.adjust_score_point_system(section)
            case XCode.CONFIGURATIONS:
                for section in line.split()[1:]:
                    trf.x_section.adjust_configuration(section)
            case XCode.ACCELERATIONS:
                trf.x_section.add_acceleration(line)
            case XCode.FORBIDDEN_PAIRS:
                trf.x_section.add_forbidden_pair(line)

    @classmethod
    def _parse_line(cls, trf: ParsedTrf, line: str) -> None:
        """Parse a line in a TRF."""
        if len(line) < 3:
            raise LineException("Line is incomplete")
        code_string = line[:3]

        try:
            cls._parse_line_player(trf, PlayerCode(code_string), line)
            return
        except ValueError:
            pass

        try:
            cls._parse_line_tournament(trf, TournamentCode(code_string), line)
            return
        except ValueError:
            pass

        try:
            cls._parse_line_team(trf, TeamCode(code_string), line)
            return
        except ValueError:
            pass

        try:
            cls._parse_line_x(trf, XCode(code_string), line)
            return
        except ValueError:
            pass

        raise LineException(f"Invalid code '{code_string}'", column=0)

    @classmethod
    def parse(cls, file_path: Path) -> ParsedTrf:
        """Parse a given TRF file returning a parsed representation."""
        trf = ParsedTrf()

        with file_path.open("r", encoding="utf-8") as fh:
            lines = [line.rstrip() for line in fh]

        for i, line in enumerate(lines):
            try:
                cls._parse_line(trf, line)
            except LineException as e:
                raise ParsingException(e.message, line=i + 1, column=e.column) from e

        trf.validate_contents()
        return trf
