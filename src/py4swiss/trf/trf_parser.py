from pathlib import Path

from py4swiss.trf.codes import PlayerCode, TeamCode, TournamentCode, XCode
from py4swiss.trf.exceptions import LineException, ParsingException
from py4swiss.trf.parsed_trf import ParsedTrf
from py4swiss.trf.sections import PlayerSection, TeamSection


class TrfParser:
    _parsed: ParsedTrf = ParsedTrf()

    @classmethod
    def _parse_line_player(cls, _: PlayerCode, line: str) -> None:
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

        for i in {3, 8, 13, 47, 52, 56, 68, 79, 84}:
            if line[i] != " ":
                raise LineException("Column of the player section line must be blank", column=i + 1)

        cls._parsed.player_sections.append(player_section)

    @classmethod
    def _parse_line_tournament(cls, code: TournamentCode, line: str) -> None:
        if len(line) < 5 or not bool(line[5:].strip()):
            return
        section = line[5:]

        match code:
            case TournamentCode.TOURNAMENT_NAME:
                cls._parsed.tournament_section.tournament_name = section
            case TournamentCode.CITY:
                cls._parsed.tournament_section.city = section
            case TournamentCode.FEDERATION:
                cls._parsed.tournament_section.federation = section
            case TournamentCode.DATE_OF_START:
                cls._parsed.tournament_section.date_of_start = section
            case TournamentCode.DATE_OF_END:
                cls._parsed.tournament_section.date_of_end = section
            case TournamentCode.NUMBER_OF_PLAYERS:
                cls._parsed.tournament_section.number_of_players = section
            case TournamentCode.NUMBER_OF_RATED_PLAYERS:
                cls._parsed.tournament_section.number_of_rated_players = section
            case TournamentCode.NUMBER_OF_TEAMS:
                cls._parsed.tournament_section.number_of_teams = section
            case TournamentCode.TYPE_OF_TOURNAMENT:
                cls._parsed.tournament_section.type_of_tournament = section
            case TournamentCode.CHIEF_ARBITER:
                cls._parsed.tournament_section.chief_arbiter = section
            case TournamentCode.DEPUTY_CHIEF_ARBITER:
                cls._parsed.tournament_section.deputy_chief_arbiter = section
            case TournamentCode.ALLOTTED_TIMES_PER_GAME_MOVE:
                cls._parsed.tournament_section.alloted_time_per_moves_game = section
            case TournamentCode.DATES_OF_THE_ROUND:
                cls._parsed.tournament_section.set_dates_of_the_round(line)

    @classmethod
    def _parse_line_team(cls, _: TeamCode, line: str) -> None:
        team_section = TeamSection()

        team_section.set_code(line)
        team_section.set_team_name(line)
        team_section.set_team_players(line)

        cls._parsed.team_sections.append(team_section)

    @classmethod
    def _parse_line_x(cls, code: XCode, line: str) -> None:
        match code:
            case XCode.ROUNDS:
                cls._parsed.x_section.set_number_of_rounds(line)
            case XCode.ZEROED_IDS:
                for section in line.split()[1:]:
                    cls._parsed.x_section.add_zeroed_id(section)
            case XCode.POINT_SYSTEM:
                for section in line.split()[1:]:
                    cls._parsed.x_section.adjust_score_point_system(section)
            case XCode.CONFIGURATIONS:
                for section in line.split()[1:]:
                    cls._parsed.x_section.adjust_configuration(section)
            case XCode.ACCELERATIONS:
                cls._parsed.x_section.add_acceleration(line)
            case XCode.FORBIDDEN_PAIRS:
                cls._parsed.x_section.add_forbidden_pair(line)

    @classmethod
    def _parse_line(cls, line: str) -> None:
        if len(line) < 3:
            raise LineException("Line is incomplete")
        code_string = line[:3]

        try:
            cls._parse_line_player(PlayerCode(code_string), line)
            return
        except ValueError:
            pass

        try:
            cls._parse_line_tournament(TournamentCode(code_string), line)
            return
        except ValueError:
            pass

        try:
            cls._parse_line_team(TeamCode(code_string), line)
            return
        except ValueError:
            pass

        try:
            cls._parse_line_x(XCode(code_string), line)
            return
        except ValueError:
            pass

        raise LineException(f"Invalid code '{code_string}'", column=0)

    @classmethod
    def parse(cls, file_path: Path) -> ParsedTrf:
        cls._parsed = ParsedTrf()

        with file_path.open("r", encoding="utf-8") as fh:
            lines = [line.rstrip() for line in fh]

        for i, line in enumerate(lines):
            try:
                cls._parse_line(line)
            except LineException as e:
                raise ParsingException(e.message, line=i + 1, column=e.column)

        cls._parsed.validate_contents()
        return cls._parsed
