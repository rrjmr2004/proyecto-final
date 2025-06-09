-- Crear la base de datos si no existe
IF DB_ID('NBA_HoopVision') IS NULL
BEGIN
    CREATE DATABASE NBA_HoopVision;
    PRINT 'Base de datos NBA_HoopVision creada.';
END
GO

USE NBA_HoopVision;
GO

PRINT 'Usando la base de datos NBA_HoopVision.';
GO
/*
-- Borrar tablas existentes en orden inverso de dependencias (MUY IMPORTANTE EL ORDEN)
PRINT 'Borrando tablas antiguas si existen...';
IF OBJECT_ID('dbo.play_by_play', 'U') IS NOT NULL DROP TABLE dbo.play_by_play;
IF OBJECT_ID('dbo.other_stats', 'U') IS NOT NULL DROP TABLE dbo.other_stats;
IF OBJECT_ID('dbo.line_score', 'U') IS NOT NULL DROP TABLE dbo.line_score;
IF OBJECT_ID('dbo.draft_history', 'U') IS NOT NULL DROP TABLE dbo.draft_history;
IF OBJECT_ID('dbo.draft_combine_stats', 'U') IS NOT NULL DROP TABLE dbo.draft_combine_stats;
IF OBJECT_ID('dbo.common_player_info', 'U') IS NOT NULL DROP TABLE dbo.common_player_info;
IF OBJECT_ID('dbo.team_details', 'U') IS NOT NULL DROP TABLE dbo.team_details;
IF OBJECT_ID('dbo.game', 'U') IS NOT NULL DROP TABLE dbo.game;
IF OBJECT_ID('dbo.player', 'U') IS NOT NULL DROP TABLE dbo.player;
IF OBJECT_ID('dbo.team', 'U') IS NOT NULL DROP TABLE dbo.team;
PRINT 'Tablas antiguas borradas.';
GO */

-- =============================================
-- ===  TABLAS MAESTRAS (IDs como NVARCHAR)  ===
-- =============================================

PRINT 'Creando tabla team...';
CREATE TABLE team (
    id NVARCHAR(50) PRIMARY KEY,       -- ID como NVARCHAR
    full_name NVARCHAR(255) NULL,
    abbreviation NVARCHAR(10) UNIQUE,
    nickname NVARCHAR(100) NULL,
    city NVARCHAR(100) NULL,
    state NVARCHAR(100) NULL,
    year_founded INT NULL              -- Mantenemos INT para año
);
GO

PRINT 'Creando tabla player...';
CREATE TABLE player (
    id NVARCHAR(50) PRIMARY KEY,       -- ID como NVARCHAR
    full_name NVARCHAR(255) NULL,
    first_name NVARCHAR(100) NULL,
    last_name NVARCHAR(100) NULL,
    is_active BIT NULL
);
GO

-- =============================================
-- ===  TABLAS DE DETALLE (IDs como NVARCHAR) ===
-- =============================================

PRINT 'Creando tabla team_details...';
CREATE TABLE team_details (
    team_id NVARCHAR(50) PRIMARY KEY,  -- ID como NVARCHAR
    abbreviation NVARCHAR(10) NULL,
    nickname NVARCHAR(100) NULL,
    yearfounded INT NULL,
    city NVARCHAR(100) NULL,
    arena NVARCHAR(100) NULL,
    arenacapacity INT NULL,
    owner NVARCHAR(255) NULL,
    generalmanager NVARCHAR(255) NULL,
    headcoach NVARCHAR(255) NULL,
    dleagueaffiliation NVARCHAR(100) NULL,
    facebook NVARCHAR(255) NULL,
    instagram NVARCHAR(255) NULL,
    twitter NVARCHAR(255) NULL,
    CONSTRAINT FK_team_details_team FOREIGN KEY (team_id) REFERENCES team(id)
);
GO

PRINT 'Creando tabla common_player_info...';
CREATE TABLE common_player_info (
    person_id NVARCHAR(50) PRIMARY KEY, -- ID como NVARCHAR
    first_name NVARCHAR(100) NULL,
    last_name NVARCHAR(100) NULL,
    display_first_last NVARCHAR(200) NULL,
    display_last_comma_first NVARCHAR(200) NULL,
    display_fi_last NVARCHAR(200) NULL,
    player_slug NVARCHAR(255) NULL,
    birthdate DATE NULL,
    school NVARCHAR(100) NULL,
    country NVARCHAR(100) NULL,
    last_affiliation NVARCHAR(200) NULL,
    height INT NULL,
    weight INT NULL,
    season_exp INT NULL,
    jersey NVARCHAR(10) NULL,
    position NVARCHAR(50) NULL,
    rosterstatus NVARCHAR(50) NULL,
    games_played_current_season_flag BIT NULL,
    team_id NVARCHAR(50) NULL,         -- ID como NVARCHAR
    team_name NVARCHAR(100) NULL,
    team_abbreviation NVARCHAR(10) NULL,
    team_code NVARCHAR(50) NULL,
    team_city NVARCHAR(100) NULL,
    playercode NVARCHAR(100) NULL,
    from_year INT NULL,
    to_year INT NULL,
    dleague_flag BIT NULL,
    nba_flag BIT NULL,
    games_played_flag BIT NULL,
    draft_year INT NULL,
    draft_round INT NULL,
    draft_number INT NULL,
    greatest_75_flag BIT NULL,
    CONSTRAINT FK_cpi_player FOREIGN KEY (person_id) REFERENCES player(id),
    CONSTRAINT FK_cpi_team FOREIGN KEY (team_id) REFERENCES team(id)
);
GO

PRINT 'Creando tabla game...';
CREATE TABLE game (
    game_id NVARCHAR(50) PRIMARY KEY, -- ID como NVARCHAR
    season_id VARCHAR(10) NULL,
    team_id_home NVARCHAR(50) NOT NULL, -- ID como NVARCHAR
    team_abbreviation_home NVARCHAR(10) NULL,
    team_name_home NVARCHAR(100) NULL,
    game_date DATE NOT NULL,
    matchup_home NVARCHAR(100) NULL,
    wl_home BIT NULL,
    min DECIMAL(5,1) NULL,
    fgm_home INT NULL, fga_home INT NULL, fg_pct_home DECIMAL(5,3) NULL,
    fg3m_home INT NULL, fg3a_home INT NULL, fg3_pct_home DECIMAL(5,3) NULL,
    ftm_home INT NULL, fta_home INT NULL, ft_pct_home DECIMAL(5,3) NULL,
    oreb_home INT NULL, dreb_home INT NULL, reb_home INT NULL, ast_home INT NULL,
    stl_home INT NULL, blk_home INT NULL, tov_home INT NULL, pf_home INT NULL,
    pts_home INT NULL, plus_minus_home INT NULL, video_available_home BIT NULL,
    team_id_away NVARCHAR(50) NOT NULL, -- ID como NVARCHAR
    team_abbreviation_away NVARCHAR(10) NULL,
    team_name_away NVARCHAR(100) NULL,
    matchup_away NVARCHAR(100) NULL,
    wl_away BIT NULL,
    fgm_away INT NULL, fga_away INT NULL, fg_pct_away DECIMAL(5,3) NULL,
    fg3m_away INT NULL, fg3a_away INT NULL, fg3_pct_away DECIMAL(5,3) NULL,
    ftm_away INT NULL, fta_away INT NULL, ft_pct_away DECIMAL(5,3) NULL,
    oreb_away INT NULL, dreb_away INT NULL, reb_away INT NULL, ast_away INT NULL,
    stl_away INT NULL, blk_away INT NULL, tov_away INT NULL, pf_away INT NULL,
    pts_away INT NULL, plus_minus_away INT NULL, video_available_away BIT NULL,
    season_type NVARCHAR(50) NULL,
    CONSTRAINT FK_game_team_home FOREIGN KEY (team_id_home) REFERENCES team(id),
    CONSTRAINT FK_game_team_away FOREIGN KEY (team_id_away) REFERENCES team(id)
);
GO

PRINT 'Creando tabla draft_history...';
CREATE TABLE draft_history (
    person_id NVARCHAR(50) NOT NULL,      -- ID como NVARCHAR
    season INT NOT NULL,
    round_number INT NULL,
    round_pick INT NULL,
    overall_pick INT NULL,                -- Mantenemos INT pero no es PK
    draft_type NVARCHAR(50) NULL,
    team_id NVARCHAR(50) NULL,          -- ID como NVARCHAR
    player_name NVARCHAR(255) NULL,
    team_city NVARCHAR(100) NULL,
    team_name NVARCHAR(100) NULL,
    team_abbreviation NVARCHAR(10) NULL,
    organization NVARCHAR(100) NULL,
    organization_type NVARCHAR(50) NULL,
    player_profile_flag BIT NULL,
    -- Clave Primaria Compuesta (Ejemplo: draft de un jugador es único)
    PRIMARY KEY (person_id, season),
    CONSTRAINT FK_draft_history_person FOREIGN KEY (person_id) REFERENCES player(id),
    CONSTRAINT FK_draft_history_team FOREIGN KEY (team_id) REFERENCES team(id)
);
GO

PRINT 'Creando tabla draft_combine_stats...';
CREATE TABLE draft_combine_stats (
    season INT NOT NULL,
    player_id NVARCHAR(50) NOT NULL,      -- ID como NVARCHAR
    first_name NVARCHAR(100) NULL,
    last_name NVARCHAR(100) NULL,
    player_name NVARCHAR(255) NULL,
    position NVARCHAR(50) NULL,
    height_wo_shoes DECIMAL(5,2) NULL, height_wo_shoes_ft_in NVARCHAR(20) NULL,
    height_w_shoes DECIMAL(5,2) NULL, height_w_shoes_ft_in NVARCHAR(20) NULL,
    weight DECIMAL(6,2) NULL, wingspan DECIMAL(5,2) NULL, wingspan_ft_in NVARCHAR(20) NULL,
    standing_reach DECIMAL(5,2) NULL, standing_reach_ft_in NVARCHAR(20) NULL,
    body_fat_pct DECIMAL(4,2) NULL, hand_length DECIMAL(4,2) NULL, hand_width DECIMAL(4,2) NULL,
    standing_vertical_leap DECIMAL(4,2) NULL, max_vertical_leap DECIMAL(4,2) NULL,
    lane_agility_time DECIMAL(5,2) NULL, modified_lane_agility_time DECIMAL(5,2) NULL,
    three_quarter_sprint DECIMAL(5,2) NULL, bench_press INT NULL,
    spot_fifteen_corner_left NVARCHAR(10) NULL, spot_fifteen_break_left NVARCHAR(10) NULL,
    spot_fifteen_top_key NVARCHAR(10) NULL, spot_fifteen_break_right NVARCHAR(10) NULL,
    spot_fifteen_corner_right NVARCHAR(10) NULL, spot_college_corner_left NVARCHAR(10) NULL,
    spot_college_break_left NVARCHAR(10) NULL, spot_college_top_key NVARCHAR(10) NULL,
    spot_college_break_right NVARCHAR(10) NULL, spot_college_corner_right NVARCHAR(10) NULL,
    spot_nba_corner_left NVARCHAR(10) NULL, spot_nba_break_left NVARCHAR(10) NULL,
    spot_nba_top_key NVARCHAR(10) NULL, spot_nba_break_right NVARCHAR(10) NULL,
    spot_nba_corner_right NVARCHAR(10) NULL, off_drib_fifteen_break_left NVARCHAR(10) NULL,
    off_drib_fifteen_top_key NVARCHAR(10) NULL, off_drib_fifteen_break_right NVARCHAR(10) NULL,
    off_drib_college_break_left NVARCHAR(10) NULL, off_drib_college_top_key NVARCHAR(10) NULL,
    off_drib_college_break_right NVARCHAR(10) NULL, on_move_fifteen NVARCHAR(10) NULL,
    on_move_college NVARCHAR(10) NULL,
    -- Clave Primaria Compuesta
    PRIMARY KEY (season, player_id),
    CONSTRAINT FK_draft_combine_stats_player FOREIGN KEY (player_id) REFERENCES player(id)
);
GO

PRINT 'Creando tabla other_stats...';
CREATE TABLE other_stats (
    game_id NVARCHAR(50) PRIMARY KEY, -- ID como NVARCHAR
    league_id NVARCHAR(10) NULL,
    team_id_home NVARCHAR(50) NULL,   -- ID como NVARCHAR
    team_abbreviation_home NVARCHAR(10) NULL, team_city_home NVARCHAR(100) NULL,
    pts_paint_home INT NULL, pts_2nd_chance_home INT NULL, pts_fb_home INT NULL,
    largest_lead_home INT NULL, lead_changes INT NULL, times_tied INT NULL,
    team_turnovers_home INT NULL, total_turnovers_home INT NULL,
    team_rebounds_home INT NULL, pts_off_to_home INT NULL,
    team_id_away NVARCHAR(50) NULL,   -- ID como NVARCHAR
    team_abbreviation_away NVARCHAR(10) NULL, team_city_away NVARCHAR(100) NULL,
    pts_paint_away INT NULL, pts_2nd_chance_away INT NULL, pts_fb_away INT NULL,
    largest_lead_away INT NULL, team_turnovers_away INT NULL,
    total_turnovers_away INT NULL, team_rebounds_away INT NULL, pts_off_to_away INT NULL,
    CONSTRAINT FK_other_stats_game FOREIGN KEY (game_id) REFERENCES game(game_id),
    CONSTRAINT FK_other_stats_team_home FOREIGN KEY (team_id_home) REFERENCES team(id),
    CONSTRAINT FK_other_stats_team_away FOREIGN KEY (team_id_away) REFERENCES team(id)
);
GO

PRINT 'Creando tabla line_score...';
CREATE TABLE line_score (
    game_id NVARCHAR(50) PRIMARY KEY, -- ID como NVARCHAR
    game_date_est DATE NULL,
    game_sequence INT NULL,
    team_id_home NVARCHAR(50) NULL,   -- ID como NVARCHAR
    team_abbreviation_home NVARCHAR(10) NULL, team_city_name_home NVARCHAR(100) NULL,
    team_nickname_home NVARCHAR(100) NULL, team_wins_losses_home NVARCHAR(20) NULL,
    pts_qtr1_home INT NULL, pts_qtr2_home INT NULL, pts_qtr3_home INT NULL, pts_qtr4_home INT NULL,
    pts_ot1_home INT NULL, pts_ot2_home INT NULL, pts_ot3_home INT NULL, pts_ot4_home INT NULL, pts_ot5_home INT NULL,
    pts_ot6_home INT NULL, pts_ot7_home INT NULL, pts_ot8_home INT NULL, pts_ot9_home INT NULL, pts_ot10_home INT NULL,
    pts_home INT NULL,
    team_id_away NVARCHAR(50) NULL,   -- ID como NVARCHAR
    team_abbreviation_away NVARCHAR(10) NULL, team_city_name_away NVARCHAR(100) NULL,
    team_nickname_away NVARCHAR(100) NULL, team_wins_losses_away NVARCHAR(20) NULL,
    pts_qtr1_away INT NULL, pts_qtr2_away INT NULL, pts_qtr3_away INT NULL, pts_qtr4_away INT NULL,
    pts_ot1_away INT NULL, pts_ot2_away INT NULL, pts_ot3_away INT NULL, pts_ot4_away INT NULL, pts_ot5_away INT NULL,
    pts_ot6_away INT NULL, pts_ot7_away INT NULL, pts_ot8_away INT NULL, pts_ot9_away INT NULL, pts_ot10_away INT NULL,
    pts_away INT NULL,
    CONSTRAINT FK_line_score_game FOREIGN KEY (game_id) REFERENCES game(game_id),
    CONSTRAINT FK_line_score_team_home FOREIGN KEY (team_id_home) REFERENCES team(id),
    CONSTRAINT FK_line_score_team_away FOREIGN KEY (team_id_away) REFERENCES team(id)
);
GO

PRINT '¡Nuevo esquema NBA_HoopVision creado exitosamente!';
GO
